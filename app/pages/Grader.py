# streamlit_grader_thai_improved.py
import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import pandas as pd
import pytesseract
import platform
import os

# ---- Tesseract path for Windows ----
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Load template ----
TEMPLATE_PATH = r"data\20250529110230_014.jpg"
template_img = Image.open(TEMPLATE_PATH).convert("RGB")
T_W, T_H = template_img.size

CHOICES = ["A", "B", "C", "D", "E"]
CHOICES_PER_Q = len(CHOICES)

# ---- Preprocess for OCR ----
def preprocess_for_ocr(img):
    """
    Preprocesses an image for better OCR results.
    """
    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    return bw

# ---- Detect bubble grid from template ----
def detect_grid_from_template(template_img, left_frac=0.35, num_choice_sets=10, num_choice_sets_col=4):
    """
    Detects the center coordinates of bubbles based on the template.
    Returns: x_centers, y_centers, x_sections
    """
    # Use a fixed crop area for the main bubble grid
    bubble_area = template_img.crop((int(T_W * left_frac), 0, T_W, T_H)).convert("L")
    arr = np.array(bubble_area)
    inv = 255 - arr  # Invert so bubbles are dark (high values)

    # Vertical projection for X-axis (columns)
    vproj = inv.sum(axis=0)
    vproj_smooth = np.convolve(vproj, np.ones(11) / 11, mode='same')
    
    x_peaks = []
    for i in range(5, len(vproj_smooth) - 5):
        if vproj_smooth[i] > vproj_smooth[i - 1] and vproj_smooth[i] > vproj_smooth[i + 1] and vproj_smooth[i] > 1000:
            x_peaks.append(i)

    def cluster(pos, tol=14):
        if not pos: return []
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

    x_centers = cluster(x_peaks, 14)

    # Separate x_centers into columns of choices
    x_sections = [
        sorted(x_centers[i:i + CHOICES_PER_Q])
        for i in range(0, len(x_centers), CHOICES_PER_Q)
    ]

    # Horizontal projection for Y-axis (rows)
    hproj = inv.sum(axis=1)
    hproj_smooth = np.convolve(hproj, np.ones(11) / 11, mode='same')
    y_peaks = []
    for i in range(5, len(hproj_smooth) - 5):
        if hproj_smooth[i] > hproj_smooth[i - 1] and hproj_smooth[i] > hproj_smooth[i + 1] and hproj_smooth[i] > 1000:
            y_peaks.append(i)
    y_centers = cluster(y_peaks, 12)

    # Adjust to full image coordinates
    x_sections_full = [[x + int(T_W * left_frac) for x in sec] for sec in x_sections]
    y_centers_full = [y for y in y_centers]

    return x_sections_full, y_centers_full

T_X_SECTIONS, T_Y_CENTERS = detect_grid_from_template(template_img)

# ---- Sample darkness at a point ----
def sample_darkness_at(img_gray_np, cx, cy, radius=10):
    """
    Samples the darkness value within a circular patch.
    """
    h, w = img_gray_np.shape
    x0, x1 = int(round(cx - radius)), int(round(cx + radius))
    y0, y1 = int(round(cy - radius)), int(round(cy + radius))
    
    # Boundary checks
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w - 1, x1), min(h - 1, y1)

    patch = img_gray_np[y0:y1 + 1, x0:x1 + 1]
    yy, xx = np.indices(patch.shape)
    mask = ((xx + x0 - cx)**2 + (yy + y0 - cy)**2) <= radius**2
    
    if mask.sum() == 0:
        return 1.0
    
    # Return mean darkness (0=dark, 1=light)
    mean_val = patch[mask].mean() / 255.0
    return mean_val

# ---- Scan one uploaded sheet ----
def scan_sheet(upload_img):
    """
    Scans an uploaded sheet to extract metadata and answers.
    """
    warped = upload_img.convert("RGB")
    left_panel = warped.crop((0, 0, int(T_W * 0.35), T_H))
    
    # Define specific OCR areas for better parsing
    info_areas = {
        "Name": (20, 110, 320, 160),
        "Subject": (20, 160, 320, 200),
        "Date": (20, 200, 320, 240),
        "Exam Room": (20, 240, 320, 280),
        "Subject Code": (20, 300, 320, 340),
        "Student ID": (20, 340, 320, 380),
    }

    info = {}
    for key, bbox in info_areas.items():
        cropped_img = left_panel.crop(bbox)
        text = pytesseract.image_to_string(preprocess_for_ocr(cropped_img), lang="eng+tha", config="--oem 3 --psm 7")
        # Clean text by removing labels and whitespace
        clean_text = text.replace(f"{key}:", "").replace("ชื่อ-นามสกุล", "").replace("วิชา", "").replace("วัน/เดือน/ปี", "").replace("ห้องสอบ", "").replace("รหัสวิชา", "").replace("รหัสประจำตัว", "").strip()
        info[key] = clean_text

    # Detect bubbles
    bubble_area = warped.convert("L")
    wg_np = np.array(bubble_area)
    answers = {}
    qnum = 1
    
    # Iterate through rows and then columns
    for y in T_Y_CENTERS:
        for col_block in T_X_SECTIONS:
            darknesses = [1.0 - sample_darkness_at(wg_np, x, y, 10) for x in col_block]
            
            # Use a threshold to determine if a bubble is marked
            selected = None
            if max(darknesses) > 0.15: # Threshold for a marked bubble
                sel_idx = np.argmax(darknesses)
                selected = CHOICES[sel_idx]
            
            answers[qnum] = selected
            qnum += 1
            
            if qnum > len(T_Y_CENTERS) * len(T_X_SECTIONS):
                break
        if qnum > len(T_Y_CENTERS) * len(T_X_SECTIONS):
            break

    # Fix question numbering
    final_answers = {}
    q_count = 1
    for y_idx, y in enumerate(T_Y_CENTERS):
        for x_idx, col_block in enumerate(T_X_SECTIONS):
            darknesses = [1.0 - sample_darkness_at(wg_np, x, y, 10) for x in col_block]
            selected = None
            if max(darknesses) > 0.15:
                sel_idx = np.argmax(darknesses)
                selected = CHOICES[sel_idx]
            final_answers[q_count] = selected
            q_count += 1
            if q_count > 60: # Limit to 60 questions
                break
        if q_count > 60:
            break
            
    return {"warped_image": warped, "info": info, "answers": final_answers}

# ---- CSV saver ----
def save_results_csv(info, answers, filename_prefix="out", output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    student_id = info.get("Student ID") or "unknown"
    subject_id = info.get("Subject Code") or "subj"
    csv_name = f"{student_id}_{subject_id}_{filename_prefix}.csv"
    csv_path = os.path.join(output_dir, csv_name)
    df = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    for k, v in info.items():
        df[k] = v
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, df

# ---- Streamlit UI ----
st.set_page_config(page_title="Thai Grader", layout="wide")
st.title("✅ Grader สำหรับกระดาษคำตอบภาษาไทย")

num_questions_estimate = st.number_input("จำนวนคำถามสูงสุด (ประมาณ)", min_value=10, max_value=200, value=60, step=1)
uploaded = st.file_uploader("Upload scanned sheet (jpg/png)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Show template (debug)"):
    st.image(template_img, caption="Template image", use_column_width=True)
    st.write("X sections:", T_X_SECTIONS)
    st.write("Y centers:", T_Y_CENTERS)

if uploaded:
    all_dfs = []
    for up in uploaded:
        st.subheader(up.name)
        try:
            upload_img = Image.open(up).convert("RGB")
        except Exception as e:
            st.error(f"Cannot open {up.name}: {e}")
            continue
        
        with st.spinner("Scanning..."):
            result = scan_sheet(upload_img)
        
        st.image(result["warped_image"], caption="Warped/Aligned sheet", use_column_width=True)
        st.markdown("**Parsed Info:**")
        st.json(result["info"])
        
        st.markdown("**Detected Answers:**")
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

