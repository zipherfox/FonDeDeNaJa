# streamlit_grader_cropped_numeric.py
import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import pandas as pd
import pytesseract
import platform
import os
import math

# ---- Tesseract path ----
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if platform.system() == "Linux":
    pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

# ---- Bubble grid ----
T_W, T_H = 2480, 3508  # A4 at 300dpi
NUM_QUESTIONS = 60
COLUMNS = 5
ROWS = math.ceil(NUM_QUESTIONS / COLUMNS)

x_centers = np.linspace(800, T_W-50, COLUMNS)  # adjust per template
y_centers = np.linspace(200, T_H-50, ROWS)

# ---- OCR crop function ----
def extract_text(image, box):
    x, y, w, h = box
    cropped = image.crop((x, y, x + w, y + h))
    text = pytesseract.image_to_string(cropped, lang="tha+eng")
    return text.strip()

# ---- Bubble detection for numeric answers ----
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

def scan_bubbles_numeric(upload_img, num_questions=NUM_QUESTIONS):
    warped_gray = np.array(upload_img.convert("L"))
    answers = {}
    qnum = 1
    for y in y_centers:
        for x in x_centers:
            darkness = 1 - sample_darkness_at(warped_gray, x, y, radius=10)
            if darkness < 0.15:
                val = None
            else:
                val = int(round(darkness * 9))  # map darkness to 0–9
            answers[qnum] = val
            qnum += 1
            if qnum > num_questions: break
        if qnum > num_questions: break
    return answers

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

# ---- Build answer table ----
def build_answer_table(answers):
    data = []
    for q, ans in answers.items():
        data.append({"Q": q, "Answer": ans})
    return pd.DataFrame(data)

# ---- Streamlit UI ----
st.set_page_config(page_title="Grader OCR Numeric", layout="wide")
st.title("📄 Grader OCR - Numeric Answers")

num_questions_estimate = st.number_input("Max questions to detect", min_value=10, max_value=200, value=NUM_QUESTIONS)
uploaded = st.file_uploader("Upload scanned sheet", type=["jpg","jpeg","png"], accept_multiple_files=True)

# --- Metadata boxes (adjust per template) ---
BOXES = {
    "Name": (100, 400, 430, 80),
    "Subject": (100, 447, 450, 80),
    "Date": (100, 520, 540, 80),
    "Exam Room": (100, 555, 560, 80),
    "Subject Code": (100, 600, 650, 80),
    "Student ID": (100, 700, 300, 80),
}

if uploaded:
    all_tables=[]
    for up in uploaded:
        st.subheader(up.name)
        try: upload_img = Image.open(up).convert("RGB")
        except Exception as e:
            st.error(f"Cannot open {up.name}: {e}")
            continue

        st.image(upload_img, caption="Uploaded sheet", use_column_width=True)

        # --- OCR metadata ---
        info={}
        st.markdown("**📌 Metadata from cropped boxes:**")
        for field, box in BOXES.items():
            text = extract_text(upload_img, box)
            info[field] = text
            st.write(f"**{field}:** {text}")
        st.json(info)

        # --- Scan numeric answers ---
        with st.spinner("Scanning bubble answers..."):
            answers = scan_bubbles_numeric(upload_img, num_questions=int(num_questions_estimate))
        st.markdown("**Detected Numeric Answers:**")
        st.write(answers)

        # --- Answer table ---
        df_table = build_answer_table(answers)
        st.markdown("**Answer Table:**")
        st.dataframe(df_table, use_container_width=True)

        # --- Save CSV ---
        csv_path, df = save_results_csv(info, answers, filename_prefix=up.name.split(".")[0])
        csv_bytes = df_table.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download Answer Table CSV", csv_bytes, f"{up.name.split('.')[0]}_answers.csv", "text/csv")
        all_tables.append(df_table)

    # --- Combined table if multiple files ---
    if len(all_tables)>1:
        combined = pd.concat(all_tables, ignore_index=True)
        csv_all = combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download combined answer table CSV", csv_all, "all_answers.csv", "text/csv")

