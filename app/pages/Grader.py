import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd
import pytesseract
import platform
import os

# === Tesseract path for Windows ===
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# === OCR metadata extraction ===
def extract_metadata_text(img: Image.Image):
    gray = img.convert("L")
    w, h = gray.size
    roi = gray.crop((0, 0, int(w*0.35), h))  # Left 35% for metadata
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(roi, config=custom_config, lang="eng+tha")
    return text

# === Parse OCR text into info fields ===
def extract_info(metadata_text):
    info = {
        "Name": "",
        "Subject": "",
        "Date": "",
        "Exam Room": "",
        "Subject Code": "",
        "Student ID": ""
    }
    for line in metadata_text.splitlines():
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
    return info

# === Generate mock answers (replace with real bubble detection) ===
def extract_answers(num_questions=30):
    return {q: np.random.randint(0, 10) for q in range(1, num_questions+1)}

# === Save CSV ===
def save_csv(info, answers, filename="upload", output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    student_id = info["Student ID"] or "unknown"
    subject_id = info["Subject Code"] or "subj"
    csv_name = f"{student_id}_{subject_id}_{filename}.csv"
    csv_path = os.path.join(output_dir, csv_name)

    df = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    for k, v in info.items():
        df[k] = v
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    return csv_path, df

# === Streamlit UI ===
st.set_page_config(page_title="Bubble Sheet OCR & Grader", layout="wide")
st.title("📝 Bubble Sheet OCR & Grader")

uploaded_files = st.file_uploader(
    "📤 Upload scanned student sheet(s)",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

if uploaded_files:
    all_results = []

    for uploaded_file in uploaded_files:
        st.divider()
        st.subheader(f"📄 File: `{uploaded_file.name}`")

        try:
            img = Image.open(uploaded_file).convert("RGB")
        except Exception as e:
            st.error(f"❌ Could not read `{uploaded_file.name}`: {e}")
            continue

        # Automatically resize large images to prevent 413
        max_dim = 2000
        if img.width > max_dim or img.height > max_dim:
            img.thumbnail((max_dim, max_dim))
            st.info(f"Image resized to fit within {max_dim}x{max_dim}")

        st.image(img, caption="Uploaded Image", use_column_width=True)

        # Extract metadata
        metadata_text = extract_metadata_text(img)
        info = extract_info(metadata_text)

        # Extract answers
        answers = extract_answers(num_questions=30)

        # Save CSV
        csv_path, df = save_csv(info, answers, filename=uploaded_file.name.split(".")[0])
        st.success(f"✅ Processed successfully! CSV saved as `{csv_path}`")

        st.markdown("**Extracted Info:**")
        st.json(info)

        st.markdown("**Answers (first 10 questions):**")
        st.write(dict(list(answers.items())[:10]))

        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv_bytes,
            f"{info['Student ID']}_result.csv",
            "text/csv"
        )

        all_results.append(df)

    if len(all_results) > 1:
        all_df = pd.concat(all_results, ignore_index=True)
        st.divider()
        st.subheader("📥 Export All Results")
        merged_csv = all_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download All Results CSV", merged_csv, "all_students_results.csv", "text/csv")

