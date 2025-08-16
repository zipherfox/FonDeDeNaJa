# streamlit_grader_no_template.py
import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import pandas as pd
import pytesseract
import platform
import os
import math

# ---- Tesseract path for Windows ----
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---- Template simulation (no real image needed) ----
T_W, T_H = 2480, 3508  # A4 at 300dpi
META_WIDTH = int(T_W*0.35)

# Bubble grid parameters
NUM_QUESTIONS = 60
CHOICES_PER_Q = 5
COLUMNS = 5  # number of horizontal question blocks
ROWS = math.ceil(NUM_QUESTIONS / COLUMNS)

# Generate x_centers and y_centers
x_centers = np.linspace(META_WIDTH+50, T_W-50, CHOICES_PER_Q*COLUMNS)
y_centers = np.linspace(200, T_H-50, ROWS)

CHOICES = ["A","B","C","D","E"]

# ---- Utility functions ----
def preprocess_ocr(img):
    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    bw = gray.point(lambda x: 0 if x<150 else 255, '1')
    return bw

def sample_darkness_at(img_gray_np, cx, cy, radius=10):
    h,w = img_gray_np.shape
    x0 = max(0, int(cx-radius))
    x1 = min(w-1, int(cx+radius))
    y0 = max(0, int(cy-radius))
    y1 = min(h-1, int(cy+radius))
    patch = img_gray_np[y0:y1+1, x0:x1+1]
    yy, xx = np.indices(patch.shape)
    mask = ((xx + x0 - cx)**2 + (yy + y0 - cy)**2) <= radius*radius
    if mask.sum() == 0: return 1.0
    return patch[mask].mean()/255.0

def scan_sheet(upload_img, num_questions=NUM_QUESTIONS):
    # --- split metadata panel ---
    meta_panel = upload_img.crop((0,0,META_WIDTH,T_H))
    meta_panel = preprocess_ocr(meta_panel)
    meta_text = pytesseract.image_to_string(meta_panel, lang="eng+tha", config="--oem 3 --psm 6")

    # parse metadata
    info = {"Name": "", "Subject": "", "Date": "", "Exam Room": "", "Subject Code": "", "Student ID": ""}
    for line in meta_text.splitlines():
        line = line.strip()
        if not line: continue
        if "ชื่อ" in line or "Name" in line: info["Name"] = line.split(":")[-1].strip()
        elif "วิชา" in line or "Subject" in line: info["Subject"] = line.split(":")[-1].strip()
        elif "วัน" in line or "Date" in line: info["Date"] = line.split(":")[-1].strip()
        elif "ห้องสอบ" in line or "Room" in line: info["Exam Room"] = line.split(":")[-1].strip()
        elif "รหัสวิชา" in line or "Subject code" in line: info["Subject Code"] = line.split(":")[-1].strip()
        elif "รหัสประจำตัว" in line or "Student" in line: info["Student ID"] = line.split(":")[-1].strip()

    # --- detect bubbles ---
    warped_gray = np.array(upload_img.convert("L"))
    answers = {}
    qnum = 1
    for y in y_centers:
        for i in range(0, len(x_centers), CHOICES_PER_Q):
            col_block = x_centers[i:i+CHOICES_PER_Q]
            darknesses = [1-sample_darkness_at(warped_gray, x, y, radius=10) for x in col_block]
            sel_idx = int(np.argmax(darknesses))
            if darknesses[sel_idx] < 0.15: selected = None
            else: selected = CHOICES[sel_idx]
            answers[qnum] = selected
            qnum += 1
            if qnum > num_questions: break
        if qnum > num_questions: break

    return {"metadata_text": meta_text, "info": info, "answers": answers, "warped_image": upload_img}

# ---- CSV saver ----
def save_results_csv(info, answers, filename_prefix="out", output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    student_id = info.get("Student ID") or "unknown"
    subject_id = info.get("Subject Code") or "subj"
    csv_name = f"{student_id}_{subject_id}_{filename_prefix}.csv"
    csv_path = os.path.join(output_dir, csv_name)
    df = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    for k,v in info.items(): df[k] = v
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, df

# ---- Streamlit UI ----
st.set_page_config(page_title="Grader", layout="wide")
st.title("Grader")

st.markdown("Upload scanned student sheets.")

num_questions_estimate = st.number_input("Max questions to detect", min_value=10, max_value=200, value=NUM_QUESTIONS)
uploaded = st.file_uploader("Upload scanned sheet", type=["jpg","jpeg","png"], accept_multiple_files=True)

if uploaded:
    all_dfs=[]
    for up in uploaded:
        st.subheader(up.name)
        try: upload_img = Image.open(up).convert("RGB")
        except Exception as e:
            st.error(f"Cannot open {up.name}: {e}")
            continue

        with st.spinner("Scanning sheet..."):
            result = scan_sheet(upload_img, num_questions=int(num_questions_estimate))

        st.image(result["warped_image"], caption="Original/processed sheet", use_column_width=True)
        st.markdown("**Extracted Metadata (OCR):**")
        st.code(result["metadata_text"][:800] + ("..." if len(result["metadata_text"])>800 else ""))
        st.markdown("**Parsed Info:**")
        st.json(result["info"])
        st.markdown("**Detected Answers:**")
        st.write(result["answers"])

        csv_path, df = save_results_csv(result["info"], result["answers"], filename_prefix=up.name.split(".")[0])
        st.success(f"Saved CSV: `{csv_path}`")
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", csv_bytes, f"{up.name.split('.')[0]}_results.csv", "text/csv")
        all_dfs.append(df)

    if len(all_dfs)>1:
        combined = pd.concat(all_dfs, ignore_index=True)
        csv_all = combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download combined CSV", csv_all, "all_results.csv", "text/csv")



