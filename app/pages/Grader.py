# streamlit_grader_thai.py
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

# ---- Utility to detect dark pixels for bubbles ----
def sample_darkness_at(img_gray_np, cx, cy, radius=10):
    h,w = img_gray_np.shape
    x0 = max(0, int(round(cx - radius)))
    x1 = min(w-1, int(round(cx + radius)))
    y0 = max(0, int(round(cy - radius)))
    y1 = min(h-1, int(round(cy + radius)))
    patch = img_gray_np[y0:y1+1, x0:x1+1]
    yy, xx = np.indices(patch.shape)
    mask = ((xx + x0 - cx)**2 + (yy + y0 - cy)**2) <= radius*radius
    if mask.sum() == 0:
        return 1.0
    mean_val = patch[mask].mean() / 255.0
    return mean_val

# ---- Scan sheet ----
def scan_sheet_from_upload(upload_img_pil, num_questions_estimate=40):
    # warp assumed done already; here we just split panels
    warped = upload_img_pil  # if warp function exists, replace here
    # 1) Split panels
    left_panel = warped.crop((0, 0, int(T_W*0.35), T_H))   # metadata
    right_panel = warped.crop((int(T_W*0.35), 0, T_W, T_H))  # bubbles

    # --- Preprocess left_panel for OCR ---
    gray = left_panel.convert("L")
    gray = ImageEnhance.Contrast(gray).enhance(2.0)
    bw = gray.point(lambda x: 0 if x<150 else 255, "1")

    # OCR Thai + English
    metadata_text = pytesseract.image_to_string(bw, lang="eng+tha", config="--oem 3 --psm 6")

    # Parse fields
    info = {"Name": "", "Subject": "", "Date": "", "Exam Room": "", "Subject Code": "", "Student ID": ""}
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

    # --- Detect bubbles ---
    wg_np = np.array(right_panel.convert("L"))
    # Split right_panel into grid
    h, w = wg_np.shape
    x_centers = np.linspace(20, w-20, CHOICES_PER_Q*6)  # crude example, adjust for template
    y_centers = np.linspace(20, h-20, 40)  # estimate 40 questions

    answers = {}
    qnum = 1
    for y in y_centers:
        for i in range(0, len(x_centers), CHOICES_PER_Q):
            col_block = x_centers[i:i+CHOICES_PER_Q]
            darknesses = [1.0 - sample_darkness_at(wg_np, x, y, radius=10) for x in col_block]
            sel_idx = int(np.argmax(darknesses))
            if darknesses[sel_idx] < 0.15:
                selected = None
            else:
                selected = CHOICES[sel_idx]
            answers[qnum] = selected
            qnum += 1
            if qnum > num_questions_estimate:
                break
        if qnum > num_questions_estimate:
            break

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
st.title("✅ Thai OCR Bubble Sheet Grader")
num_questions_estimate = st.number_input("Max questions estimate", min_value=10, max_value=200, value=40)
uploaded = st.file_uploader("Upload scanned sheet (jpg/png)", type=["jpg","jpeg","png"], accept_multiple_files=True)

if uploaded:
    all_dfs=[]
    for up in uploaded:
        st.subheader(up.name)
        try:
            upload_img = Image.open(up).convert("RGB")
        except:
            st.error(f"Cannot open {up.name}")
            continue
        result = scan_sheet_from_upload(upload_img, num_questions_estimate=int(num_questions_estimate))
        st.image(result["warped_image"], caption="Warped sheet / panels", use_column_width=True)
        st.markdown("**Metadata OCR (Thai + English):**")
        st.code(result["metadata_text"][:800])
        st.markdown("**Parsed Info:**")
        st.json(result["info"])
        st.markdown("**Detected Answers (first 50):**")
        st.write({k:v for k,v in list(result["answers"].items())[:50]})
        csv_path, df = save_results_csv(result["info"], result["answers"], filename_prefix=up.name.split(".")[0])
        st.success(f"Saved CSV: {csv_path}")
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", csv_bytes, f"{up.name.split('.')[0]}_results.csv", "text/csv")
        all_dfs.append(df)

    if len(all_dfs) > 1:
        combined = pd.concat(all_dfs, ignore_index=True)
        csv_all = combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download combined CSV", csv_all, "all_results.csv", "text/csv")


