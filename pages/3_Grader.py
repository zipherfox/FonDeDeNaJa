import streamlit as st
import cv2
import numpy as np
import pandas as pd
import pytesseract
import platform

# Automatically set tesseract path if on Windows
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from bubble_grader_frontend import grade_sheet  # rename this to your backend file name

st.set_page_config(page_title="Bubble Sheet Grader", layout="wide")
st.title("📝 Bubble Sheet Grader")

# === Load golden answer key ===
ANSWER_KEY_PATH = "20250529110230_014.jpg"
answer_key_img = cv2.imread(ANSWER_KEY_PATH)
if answer_key_img is None:
    st.error("❌ Could not load answer key image.")
    st.stop()

# === Upload student sheet(s) ===
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

        # === Show Metadata ===
        st.markdown(f"**👤 Name:** `{name}`")
        st.markdown(f"**🆔 Student ID:** `{student_id}`")

        # === Show Summary ===
        st.markdown("### 📊 Result Summary")
        st.write(f"✅ Correct: {summary['correct']}")
        st.write(f"❌ Wrong: {summary['wrong']}")
        st.write(f"❓ Missing: {summary['missing']}")
        st.write(f"⚠️ Multiple: {summary['multiple']}")

        # === Show Table and CSV ===
        df = pd.DataFrame(report, columns=["Question", "Selected", "Result"])
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV Report", csv, f"{student_id}_result.csv", "text/csv")

        # Store for optional global export
        df['Name'] = name
        df['Student ID'] = student_id
        all_results.append(df)

    # === Optional: Download all results merged
    if len(all_results) > 1:
        all_df = pd.concat(all_results, ignore_index=True)
        st.divider()
        st.subheader("📥 Export All Results")
        merged_csv = all_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download All Results CSV", merged_csv, "all_students_results.csv", "text/csv")



