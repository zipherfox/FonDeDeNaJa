# streamlit_grader_template.py
import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import pytesseract
import platform
import os
import io
import math

# ---- Tesseract path for Windows ----
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Load template (the image you provided) ----
TEMPLATE_PATH = r"data\20250529110230_014.jpg"
template_img = Image.open(TEMPLATE_PATH).convert("RGB")
T_W, T_H = template_img.size

# ---- Utility: compute centroid of dark pixels in a rectangular window (PIL Image) ----
def centroid_dark_window(img_gray_np, x, y, w, h, thresh=80):
    win = img_gray_np[y:y+h, x:x+w]
    mask = win < thresh
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return None
    cx = x + xs.mean()
    cy = y + ys.mean()
    return (cx, cy)

# ---- Precompute template registration markers by scanning template corners ----
def find_template_markers(template_img):
    gray = template_img.convert("L")
    g_np = np.array(gray)
    W, H = template_img.size
    # windows chosen to capture the small black registration marks from the template
    windows = {
        "top-left": (0, 0, 220, 220),
        "top-right": (W-220, 0, 220, 220),
        "bottom-left": (0, H-220, 220, 220),
        "bottom-right": (W-420, H-420, 420, 420),
    }
    markers = {}
    for name, (x,y,w,h) in windows.items():
        c = centroid_dark_window(g_np, x, y, w, h, thresh=80)
        if c is None:
            # fallback to center of window if detection fails
            c = (x + w/2, y + h/2)
        markers[name] = c
    return markers

TEMPLATE_MARKERS = find_template_markers(template_img)
# Order template marker points as: TL, TR, BL, BR
template_pts = np.array([
    TEMPLATE_MARKERS["top-left"],
    TEMPLATE_MARKERS["top-right"],
    TEMPLATE_MARKERS["bottom-left"],
    TEMPLATE_MARKERS["bottom-right"]
], dtype=np.float32)

# ---- Compute perspective coefficients for PIL transform
# Given src_pts (4x2) and dst_pts (4x2), compute 3x3 H so that dst ~ H * src (homogeneous)
def find_perspective_coeffs(src_pts, dst_pts):
    # We compute matrix A * h = b to solve for h (8 unknowns; 9th is 1)
    A = []
    b = []
    for (xs, ys), (xd, yd) in zip(src_pts, dst_pts):
        A.append([xs, ys, 1, 0, 0, 0, -xd*xs, -xd*ys])
        b.append(xd)
        A.append([0, 0, 0, xs, ys, 1, -yd*xs, -yd*ys])
        b.append(yd)
    A = np.array(A, dtype=np.float64)
    b = np.array(b, dtype=np.float64)
    # least squares
    h, *_ = np.linalg.lstsq(A, b, rcond=None)
    coeffs = np.append(h, 1).reshape(3,3)
    return coeffs

# Convert 3x3 H to PIL perspective 8-tuple mapping output->input:
# PIL expects coefficients (a,b,c,d,e,f,g,h) where
# x_src = (a x_dst + b y_dst + c) / (g x_dst + h y_dst + 1)
# y_src = (d x_dst + e y_dst + f) / (g x_dst + h y_dst + 1)
def matrix_to_pil_coeffs(H):
    H = H / H[2,2]
    a,b,c = H[0,0], H[0,1], H[0,2]
    d,e,f = H[1,0], H[1,1], H[1,2]
    g,h,_ = H[2,0], H[2,1], H[2,2]
    return (a,b,c,d,e,f,g,h)

# ---- Find markers in uploaded image using corner windows like template detection ----
def find_markers_in_upload(img):
    gray = img.convert("L")
    g_np = np.array(gray)
    W, H = img.size
    # Use same relative windows (scaled) as template to search for dark registration marks
    windows = {
        "top-left": (0, 0, min(240, W//4), min(240, H//4)),
        "top-right": (max(W-240, W//2), 0, min(240, W//2), min(240, H//4)),
        "bottom-left": (0, max(H-240, H//2), min(240, W//4), min(240, H//2)),
        "bottom-right": (max(W-420, W*2//3), max(H-420, H*2//3), min(420, W//3), min(420, H//3)),
    }
    markers = {}
    for name,(x,y,w,h) in windows.items():
        if x<0: x=0
        if y<0: y=0
        if x+w>W: w=W-x
        if y+h>H: h=H-y
        c = centroid_dark_window(g_np, int(x), int(y), int(w), int(h), thresh=90)
        if c is None:
            c = (x + w/2, y + h/2)
        markers[name] = c
    return markers

# ---- Automatic bubble grid detection on the template ----
# Detect vertical peaks (columns) and horizontal peaks (rows) from the bubble region of template
def detect_grid_from_template(template_img, left_frac=0.33, choices_per_question=5):
    gray = template_img.convert("L")
    g_np = np.array(gray)
    Ht, Wt = g_np.shape
    x0 = int(Wt * left_frac)
    bubble_area = g_np[:, x0:]
    # invert brightness so dark circle edges are high
    inv = 255 - bubble_area
    # vertical projection (sum over rows) -> find columns of bubbles
    vproj = inv.sum(axis=0).astype(np.float32)
    # smooth projection with small window
    kernel = np.ones(11)/11
    vsm = np.convolve(vproj, kernel, mode='same')
    # find peaks: local maxima with threshold
    cols = []
    for i in range(5, len(vsm)-5):
        if vsm[i] > vsm[i-1] and vsm[i] > vsm[i+1] and vsm[i] > vsm.mean()*1.1:
            cols.append(i + x0)
    # cluster nearby peaks
    def cluster_positions(pos, tol=12):
        if not pos:
            return []
        pos_sorted = sorted(pos)
        clusters = []
        cur = [pos_sorted[0]]
        for p in pos_sorted[1:]:
            if p - cur[-1] <= tol:
                cur.append(p)
            else:
                clusters.append(int(round(np.mean(cur))))
                cur = [p]
        clusters.append(int(round(np.mean(cur))))
        return clusters
    x_centers = cluster_positions(cols, tol=14)

    # horizontal projection -> find rows
    hproj = inv.sum(axis=1).astype(np.float32)
    hsm = np.convolve(hproj, kernel, mode='same')
    rows = []
    for i in range(5, len(hsm)-5):
        if hsm[i] > hsm[i-1] and hsm[i] > hsm[i+1] and hsm[i] > hsm.mean()*1.05:
            rows.append(i)
    y_centers = cluster_positions(rows, tol=12)

    # Ensure we have sensible counts by filtering:
    if len(x_centers) < choices_per_question:
        # fallback: try splitting bubble area width into groups of `choices_per_question`
        width = (Wt - x0)
        approx_per_choice = width // (choices_per_question * 6) or 30
        # create grid of choices_per_question * some columns
        x_centers = [x0 + approx_per_choice*(i+1) for i in range(choices_per_question*6)]
    if len(y_centers) < 5:
        # fallback: create vertical grid
        step = Ht // 18
        y_centers = [step*(i+2) for i in range(18)]

    # sort and return
    x_centers = sorted(x_centers)
    y_centers = sorted(y_centers)
    return x_centers, y_centers

# Precompute template grid
T_X_CENTERS, T_Y_CENTERS = detect_grid_from_template(template_img, left_frac=0.33, choices_per_question=5)

# The typical sheet in this template has 5 choices per question (A-E).
CHOICES = ["A","B","C","D","E"]
CHOICES_PER_Q = len(CHOICES)

# ---- function to warp uploaded image to template coords using perspective ----
def warp_to_template(img_upload, upload_markers, template_pts):
    # upload_markers: dict with "top-left","top-right","bottom-left","bottom-right"
    src_pts = np.array([
        upload_markers["top-left"],
        upload_markers["top-right"],
        upload_markers["bottom-left"],
        upload_markers["bottom-right"]
    ], dtype=np.float32)
    dst_pts = template_pts.astype(np.float32)
    # We need an H mapping dst -> src (PIL expects mapping from output coords to input coords)
    # Compute homography mapping dst -> src, i.e. for each dst_pt, we want src_pt,
    # so solve using pairs (dst -> src)
    H = find_perspective_coeffs(dst_pts, src_pts)  # maps dst -> src
    coeffs = matrix_to_pil_coeffs(H)
    # Apply PIL perspective transform: size = template size
    warped = img_upload.transform((T_W, T_H), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    return warped

# ---- detect filled bubble at center by sampling a small circular region ----
def sample_darkness_at(img_gray_np, cx, cy, radius=10):
    h,w = img_gray_np.shape
    x0 = int(round(cx - radius))
    x1 = int(round(cx + radius))
    y0 = int(round(cy - radius))
    y1 = int(round(cy + radius))
    if x0<0: x0=0
    if y0<0: y0=0
    if x1>=w: x1=w-1
    if y1>=h: y1=h-1
    patch = img_gray_np[y0:y1+1, x0:x1+1]
    yy, xx = np.indices(patch.shape)
    mask = ((xx + x0 - cx)**2 + (yy + y0 - cy)**2) <= radius*radius
    if mask.sum() == 0:
        return 1.0
    mean_val = patch[mask].mean() / 255.0  # normalized brightness (0 dark - 1 bright)
    return mean_val

# ---- Main RN: scan one uploaded image and return info + answers ----
def scan_sheet_from_upload(upload_img_pil, num_questions_estimate=40):
    # 1) find markers in upload
    upload_markers = find_markers_in_upload(upload_img_pil)
    # 2) warp to template coords
    warped = warp_to_template(upload_img_pil, upload_markers, template_pts)
    # 3) perform OCR metadata on left panel
    left_panel = warped.crop((0, 0, int(T_W*0.35), T_H))
    metadata_text = pytesseract.image_to_string(left_panel, config=r'--oem 3 --psm 6', lang="eng+tha")
    # parse info fields
    info = {
        "Name": "", "Subject": "", "Date": "", "Exam Room": "", "Subject Code": "", "Student ID": ""
    }
    for line in metadata_text.splitlines():
        line = line.strip()
        if not line: continue
        if "ชื่อ" in line or "Name" in line:
            info["Name"] = line.split(":")[-1].strip()
        elif "วิชา" in line or "Subject" in line:
            info["Subject"] = line.split(":")[-1].strip()
        elif "วัน" in line or "Date" in line:
            info["Date"] = line.split(":")[-1].strip()
        elif "ห้องสอบ" in line or "Room" in line:
            info["Exam Room"] = line.split(":")[-1].strip()
        elif "รหัสวิชา" in line or "Subject code" in line:
            info["Subject Code"] = line.split(":")[-1].strip()
        elif "รหัสประจำตัว" in line or "Student" in line:
            info["Student ID"] = line.split(":")[-1].strip()

    # 4) detect bubbles from the warped image using template grid centers (T_X_CENTERS, T_Y_CENTERS)
    warped_gray = warped.convert("L")
    wg_np = np.array(warped_gray)
    # refinement: recompute precise x_centers and y_centers by local maxima in template's neighborhoods
    x_centers = []
    for x in T_X_CENTERS:
        # small local search to place center at local darkest x within +/-8 px
        xv = int(round(x))
        lo = max(0, xv-8); hi = min(T_W-1, xv+8)
        col = wg_np[:, lo:hi+1].mean(axis=1)
        ypeak = np.argmin(col)  # darkest stripe - but for x we want column projection -> find column darkest across rows around bubble rows; simple approach:
        # instead find column location by searching columns inside that window where vertical sum of dark is max
        col_sum = (255 - wg_np[:, lo:hi+1]).sum(axis=0)
        best_col_offset = int(np.argmax(col_sum))
        x_centers.append(lo + best_col_offset)
    y_centers = []
    for y in T_Y_CENTERS:
        yv = int(round(y))
        lo = max(0, yv-8); hi = min(T_H-1, yv+8)
        row_sum = (255 - wg_np[lo:hi+1, :]).sum(axis=1)
        best_row_offset = int(np.argmax(row_sum))
        y_centers.append(lo + best_row_offset)

    # remove duplicates and sort
    x_centers = sorted(list(dict.fromkeys([int(round(x)) for x in x_centers])))
    y_centers = sorted(list(dict.fromkeys([int(round(y)) for y in y_centers])))

    # If automatic centers are suspicious, fallback to template centers
    if len(x_centers) < 5:
        x_centers = T_X_CENTERS.copy()
    if len(y_centers) < 5:
        y_centers = T_Y_CENTERS.copy()

    # Now build questions by grouping x_centers into chunks of CHOICES_PER_Q (left->right)
    # The sheet typically lays out many columns of question-groups horizontally.
    # We'll split the sorted list of x_centers into groups of size choices_per_question repeating left->right.
    xc = x_centers
    # Find clusters of columns that represent a single question's choices: cluster by proximity into groups
    # Simple method: compute gap between consecutive x's and cut when gap>median*1.6
    gaps = np.diff(xc) if len(xc)>1 else np.array([50])
    if len(gaps)>0:
        cut_thresh = np.median(gaps)*1.6
    else:
        cut_thresh = 50
    groups = []
    cur = [xc[0]]
    for xi in xc[1:]:
        if xi - cur[-1] <= cut_thresh:
            cur.append(xi)
        else:
            groups.append(cur)
            cur = [xi]
    groups.append(cur)
    # flatten groups -> ensure groups have CHOICES_PER_Q members; if a group is larger, break into subgroups
    final_choice_cols = []
    for g in groups:
        if len(g) == CHOICES_PER_Q:
            final_choice_cols.append(g)
        elif len(g) > CHOICES_PER_Q:
            # break into contiguous chunks
            for i in range(0, len(g), CHOICES_PER_Q):
                chunk = g[i:i+CHOICES_PER_Q]
                if len(chunk) == CHOICES_PER_Q:
                    final_choice_cols.append(chunk)
        else:
            # too small, try to skip
            continue

    # Now for rows y_centers and for each column-block, we have CHOICES_PER_Q x positions -> questions per row = len(final_choice_cols)
    answers = {}
    qnum = 1
    for y in y_centers:
        for col_block in final_choice_cols:
            # for this (row, col_block) we have CHOICES_PER_Q centers for A..E
            darknesses = []
            for x in col_block:
                mean_b = sample_darkness_at(wg_np, x, y, radius=10)  # mean brightness 0..1
                darknesses.append(1.0 - mean_b)  # darkness 0..1 (1 dark means filled)
            # decide selected choice: pick index with darkness > threshold and max
            sel_idx = int(np.argmax(darknesses))
            # if max darkness is not significantly higher than others, consider no answer
            if darknesses[sel_idx] < 0.15:
                selected = None
            else:
                selected = CHOICES[sel_idx]
            answers[qnum] = selected
            qnum += 1
            # stop if we reached an estimated number
            if qnum > num_questions_estimate:
                break
        if qnum > num_questions_estimate:
            break

    # Trim answers to num_questions_estimate
    answers = {k:v for k,v in answers.items() if k <= num_questions_estimate}

    return {
        "warped_image": warped,
        "metadata_text": metadata_text,
        "info": info,
        "answers": answers
    }

# ---- CSV saver ----
def save_results_csv(info, answers, filename_prefix="out", output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    student_id = info.get("Student ID") or "unknown"
    subject_id = info.get("Subject Code") or "subj"
    csv_name = f"{student_id}_{subject_id}_{filename_prefix}.csv"
    csv_path = os.path.join(output_dir, csv_name)
    df = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    for k,v in info.items():
        df[k] = v
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, df

# ---- Streamlit UI ----
st.set_page_config(page_title="Template Grader (auto-align & detect)", layout="wide")
st.title("✅ Grader tuned to your template")

st.markdown("Upload a scanned student sheet. The code will auto-align to the template, detect filled bubbles, extract metadata and let you download CSV.")

num_questions_estimate = st.number_input("Max number of questions to detect (estimate)", min_value=10, max_value=200, value=60, step=1)
uploaded = st.file_uploader("Upload scanned sheet (jpg/png)", type=["jpg","jpeg","png"], accept_multiple_files=True)

if st.button("Show template markers (debug)"):
    st.write("Template size:", TEMPLATE_PATH, "→", (T_W, T_H))
    st.write("Template registration markers (approx):", TEMPLATE_MARKERS)
    st.write("Detected template grid centers: X count =", len(T_X_CENTERS), "Y count =", len(T_Y_CENTERS))
    st.image(template_img, caption="Template image", use_column_width=True)

if uploaded:
    all_dfs=[]
    for up in uploaded:
        st.subheader(up.name)
        try:
            upload_img = Image.open(up).convert("RGB")
        except Exception as e:
            st.error(f"Cannot open {up.name}: {e}")
            continue
        # Immediately resize client-large images to reduce upload memory (this occurs after upload)
        max_dim = 4000
        if upload_img.width > max_dim or upload_img.height > max_dim:
            upload_img.thumbnail((max_dim, max_dim))
            st.info("Image resized to fit within %dx%d" % (max_dim, max_dim))

        with st.spinner("Scanning and aligning..."):
            result = scan_sheet_from_upload(upload_img, num_questions_estimate=int(num_questions_estimate))
        st.image(result["warped_image"], caption="Warped to template coordinates", use_column_width=True)
        st.markdown("**Extracted metadata text (raw OCR):**")
        st.code(result["metadata_text"][:800] + ("..." if len(result["metadata_text"])>800 else ""))
        st.markdown("**Parsed Info:**")
        st.json(result["info"])
        st.markdown("**Detected Answers (first 100):**")
        st.write(result["answers"])

        csv_path, df = save_results_csv(result["info"], result["answers"], filename_prefix=up.name.split(".")[0])
        st.success(f"Saved CSV: `{csv_path}`")
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", csv_bytes, f"{up.name.split('.')[0]}_results.csv", "text/csv")
        all_dfs.append(df)

    if len(all_dfs) > 1:
        combined = pd.concat(all_dfs, ignore_index=True)
        csv_all = combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download combined CSV", csv_all, "all_results.csv", "text/csv")



