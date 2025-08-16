import streamlit as st
from liberty import mainload, sidebar
import cv2
import pytesseract
import pandas as pd
import numpy as np
import os
import platform

# Initialize Streamlit layout
mainload()
sidebar()
st.title("Upload Page")
st.write("Please upload your files here.")

def extract_info_and_answers(image_path, num_questions=30, output_dir="results"):
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"❌ Cannot read {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OCR for metadata (left panel)
    h, w = gray.shape
    left_panel = gray[:, :int(w*0.35)]  # assume metadata in left 35% of sheet
    metadata_text = pytesseract.image_to_string(left_panel, lang="eng+tha")

    # Capture fields
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

    # Extract answers (mocked here)
    answers = {q: np.random.randint(0, 10) for q in range(1, num_questions+1)}

    # Save CSV
    os.makedirs(output_dir, exist_ok=True)
    student_id = info["Student ID"] or "unknown"
    subject_id = info["Subject Code"] or "subj"
    csv_name = f"{student_id}_{subject_id}.csv"
    csv_path = os.path.join(output_dir, csv_name)

    df = pd.DataFrame(list(answers.items()), columns=["Question", "Answer"])
    for k, v in info.items():
        df[k] = v
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    return info, answers, csv_path

# Streamlit file uploader
uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    # Preview image
    st.write("Preview:")
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

    # Save temporarily to disk for OpenCV
    temp_path = os.path.join("temp_upload", uploaded_file.name)
    os.makedirs("temp_upload", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Run extraction
    try:
        info, answers, csv_path = extract_info_and_answers(temp_path)
        st.success(f"File uploaded and processed successfully! CSV saved as `{csv_path}`")
        st.write("**Extracted Info:**", info)
        st.write("**Answers (first 10 questions):**", dict(list(answers.items())[:10]))
    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
