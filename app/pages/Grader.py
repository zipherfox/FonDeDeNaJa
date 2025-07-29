import streamlit as st
import cv2
import numpy as np
import pandas as pd
import pytesseract
import platform
import re

# === Set tesseract path for Windows ===
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# === Helper function: OCR metadata (name/ID) ===
def extract_metadata_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    roi = gray[0:200, 0:1000]  # Adjust ROI for your layout
    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(roi, config=custom_config)
    return text

def extract_name_and_id(text):
    name_match = re.search(r"(?:Name|ชื่อ)\s*[:\-]?\s*(.+)", text, re.IGNORECASE)
    id_match = re.search(r"(?:ID|รหัส)\s*[:\-]?\s*(\d+)", text, re.IGNORECASE)
    name = name_match.group(1).strip() if name_match else "Unknown"
    student_id = id_match.group(1).strip() if id_match else "Unknown"
    return name, student_id

# === Dummy bubble grading function ===
def grade_sheet(student_img, answer_key_img):
    # -- Your actual grading logic here --
    # Simulate answers
    answers = []
    correct_count = 0
    wrong_count = 0
    missing_count = 0
    multiple_count = 0

    for i in range(1, 21):
        selected = "A"  # Dummy selection
        correct = "A"   # Dummy correct
        result = "✔️" if selected == correct else "❌"
        answers.append((i, selected, result))
        if result == "✔️":
            correct_count += 1
        else:
            wrong_count += 1

    text = extract_metadata_text(student_img)
    name, student_id = extract_name_and_id(text)

    summary = {
        "correct": correct_count,
        "wrong": wrong_count,
        "missing": missing_count,
        "multiple": multiple_count,
    }

    return answers, summary, name, student_id

# === Streamlit UI ===
st.set_page_config(page_title="Bubble Sheet Grader", layout="wide")
st.title("📝 Bubble Sheet Grader")

ANSWER_KEY_PATH = "20250529110230_014.jpg"
answer_key_img = cv2.imread(ANSWER_KEY_PATH)
if answer_key_img is None:
    st.error("❌ Could not load answer key image.")
    st.stop()

uploaded_files = st.file_uploader("📤 Upload scanned student sheet(s)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    all_results = []

    for uploaded_file in uploaded_files:
        st.divider()
        st.subheader(f"📄 File: `{uploaded_file.name}`")

        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        student_img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        with st.spinner("🔍 Grading..."):
            try:
                report, summary, name, student_id = grade_sheet(student_img, answer_key_img)
            except Exception as e:
                st.error(f"❌ Error during grading `{uploaded_file.name}`: {e}")
                continue

        st.markdown(f"**👤 Name:** `{name}`")
        st.markdown(f"**🆔 Student ID:** `{student_id}`")

        st.markdown("### 📊 Result Summary")
        st.write(f"✅ Correct: {summary['correct']}")
        st.write(f"❌ Wrong: {summary['wrong']}")
        st.write(f"❓ Missing: {summary['missing']}")
        st.write(f"⚠️ Multiple: {summary['multiple']}")

        df = pd.DataFrame(report, columns=["Question", "Selected", "Result"])
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV Report", csv, f"{student_id}_result.csv", "text/csv")

        df['Name'] = name
        df['Student ID'] = student_id
        all_results.append(df)

    if len(all_results) > 1:
        all_df = pd.concat(all_results, ignore_index=True)
        st.divider()
        st.subheader("📥 Export All Results")
        merged_csv = all_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download All Results CSV", merged_csv, "all_students_results.csv", "text/csv")

