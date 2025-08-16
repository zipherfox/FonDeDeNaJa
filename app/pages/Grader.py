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

CHOICES = ["A","B","C","D","E"]
CHOICES_PER_Q = len(CHOICES)

# ---- Preprocess for OCR ----
def preprocess_for_ocr(img):
    gray = img.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    bw = gray.point(lambda x: 0 if x < 150 else 255, '1')
    return bw

# ---- Detect bubble grid from template ----
def detect_grid_from_template(template_img, left_frac=0.35):
    bubble_area = template_img.crop((int(T_W*left_frac), 0, T_W, T_H)).convert("L")
    arr = np.array(bubble_area)
    inv = 255 - arr  # bubbles dark -> high
    # vertical projection → columns
    vproj = inv.sum(axis=0)
    vproj_smooth = np.convolve(vproj, np.ones(11)/11, mode='same')
    x_peaks = []
    for i in range(5,len(vproj_smooth)-5):
        if vproj_smooth[i] > vproj_smooth[i-1] and vproj_smooth[i] > vproj_smooth[i+1]:
            x_peaks.append(i)
    # cluster nearby peaks
    def cluster(pos,tol=12):
        if not pos: return []
        pos_sorted = sorted(pos)
        clusters=[]
        cur=[pos_sorted[0]]
        for p in pos_sorted[1:]:
            if p-cur[-1]<=tol:
                cur.append(p)
            else:
                clusters.append(int(round(np.mean(cur))))
                cur=[p]
        clusters.append(int(round(np.mean(cur))))
        return clusters
    x_centers = cluster(x_peaks,14)
    # horizontal projection → rows
    hproj = inv.sum(axis=1)
    hproj_smooth = np.convolve(hproj, np.ones(11)/11, mode='same')
    y_peaks = []
    for i in range(5,len(hproj_smooth)-5):
        if hproj_smooth[i] > hproj_smooth[i-1] and hproj_smooth[i] > hproj_smooth[i+1]:
            y_peaks.append(i)
    y_centers = cluster(y_peaks,12)
    # adjust to full image coordinates
    x_centers_full = [x+int(T_W*left_frac) for x in x_centers]
    return sorted(x_centers_full), sorted(y_centers)

T_X_CENTERS, T_Y_CENTERS = detect_grid_from_template(template_img)

# ---- Sample darkness at a point ----
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
    mean_val = patch[mask].mean() / 255.0
    return mean_val

# ---- Scan one uploaded sheet ----
def scan_sheet(upload_img, num_questions_estimate=40):
    # warp skipped for simplicity (assume template-aligned scan)
    warped = upload_img.convert("RGB")
    left_panel = warped.crop((0,0,int(T_W*0.35),T_H))
    left_panel_bw = preprocess_for_ocr(left_panel)
    metadata_text = pytesseract.image_to_string(left_panel_bw, lang="eng+tha", config="--oem 3 --psm 6")
    # parse info
    info = {"Name":"","Subject":"","Date":"","Exam Room":"","Subject Code":"","Student ID":""}
    for line in metadata_text.splitlines():
        line=line.strip()
        if not line: continue
        if "ชื่อ" in line or "Name" in line: info["Name"]=line.split(":")[-1].strip()
        elif "วิชา" in line or "Subject" in line: info["Subject"]=line.split(":")[-1].strip()
        elif "วัน" in line or "Date" in line: info["Date"]=line.split(":")[-1].strip()
        elif "ห้องสอบ" in line or "Room" in line: info["Exam Room"]=line.split(":")[-1].strip()
        elif "รหัสวิชา" in line or "Subject code" in line: info["Subject Code"]=line.split(":")[-1].strip()
        elif "รหัสประจำตัว" in line or "Student" in line: info["Student ID"]=line.split(":")[-1].strip()
    # detect bubbles
    bubble_area = warped.crop((int(T_W*0.35),0,T_W,T_H)).convert("L")
    wg_np = np.array(bubble_area)
    answers={}
    qnum=1
    for y in T_Y_CENTERS:
        for i in range(0,len(T_X_CENTERS),CHOICES_PER_Q):
            col_block = T_X_CENTERS[i:i+CHOICES_PER_Q]
            darknesses = [1.0-sample_darkness_at(wg_np,x,y,10) for x in col_block]
            sel_idx=int(np.argmax(darknesses))
            selected = None if darknesses[sel_idx]<0.15 else CHOICES[sel_idx]
            answers[qnum]=selected
            qnum+=1
            if qnum>num_questions_estimate: break
        if qnum>num_questions_estimate: break
    answers={k:v for k,v in answers.items() if k<=num_questions_estimate}
    return {"warped_image":warped,"metadata_text":metadata_text,"info":info,"answers":answers}

# ---- CSV saver ----
def save_results_csv(info,answers,filename_prefix="out",output_dir="results"):
    os.makedirs(output_dir,exist_ok=True)
    student_id = info.get("Student ID") or "unknown"
    subject_id = info.get("Subject Code") or "subj"
    csv_name=f"{student_id}_{subject_id}_{filename_prefix}.csv"
    csv_path=os.path.join(output_dir,csv_name)
    df=pd.DataFrame(list(answers.items()),columns=["Question","Answer"])
    for k,v in info.items(): df[k]=v
    df.to_csv(csv_path,index=False,encoding="utf-8-sig")
    return csv_path,df

# ---- Streamlit UI ----
st.set_page_config(page_title="Thai Grader",layout="wide")
st.title("✅ Grader สำหรับกระดาษคำตอบภาษาไทย")

num_questions_estimate=st.number_input("จำนวนคำถามสูงสุด (ประมาณ)",min_value=10,max_value=200,value=60,step=1)
uploaded=st.file_uploader("Upload scanned sheet (jpg/png)",type=["jpg","jpeg","png"],accept_multiple_files=True)

if st.button("Show template (debug)"):
    st.image(template_img,caption="Template image",use_column_width=True)
    st.write("X centers:",T_X_CENTERS)
    st.write("Y centers:",T_Y_CENTERS)

if uploaded:
    all_dfs=[]
    for up in uploaded:
        st.subheader(up.name)
        try: upload_img = Image.open(up).convert("RGB")
        except Exception as e:
            st.error(f"Cannot open {up.name}: {e}")
            continue
        with st.spinner("Scanning..."):
            result=scan_sheet(upload_img,num_questions_estimate)
        st.image(result["warped_image"],caption="Warped/Aligned sheet",use_column_width=True)
        st.markdown("**Metadata OCR (Thai+Eng):**")
        st.code(result["metadata_text"][:800]+("..." if len(result["metadata_text"])>800 else ""))
        st.markdown("**Parsed Info:**")
        st.json(result["info"])
        st.markdown("**Detected Answers:**")
        st.write(result["answers"])
        csv_path, df = save_results_csv(result["info"],result["answers"],filename_prefix=up.name.split(".")[0])
        st.success(f"Saved CSV: `{csv_path}`")
        csv_bytes=df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV",csv_bytes,f"{up.name.split('.')[0]}_results.csv","text/csv")
        all_dfs.append(df)
    if len(all_dfs)>1:
        combined=pd.concat(all_dfs,ignore_index=True)
        csv_all=combined.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download combined CSV",csv_all,"all_results.csv","text/csv")


