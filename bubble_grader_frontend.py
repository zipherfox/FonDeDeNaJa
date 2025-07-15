import cv2
import numpy as np
import pytesseract

def extract_metadata(img):
    h, w = img.shape[:2]
    name_region = img[0:100, 0:int(w * 0.6)]
    id_region = img[0:100, int(w * 0.6):w]

    def preprocess_text_region(region):
        gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    name_thresh = preprocess_text_region(name_region)
    id_thresh = preprocess_text_region(id_region)

    name = pytesseract.image_to_string(name_thresh, config="--psm 6").strip()
    student_id = pytesseract.image_to_string(id_thresh, config="--psm 7 -c tessedit_char_whitelist=0123456789").strip()

    name = name if name else "Unknown"
    student_id = student_id if student_id else "Unknown"
    return name, student_id

def extract_bubbles(thresh_img):
    contours, _ = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bubbles = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 20 <= w <= 40 and 20 <= h <= 40 and 0.9 <= w/h <= 1.1:
            bubbles.append((c, y, x))  # Store position for sorting

    # Sort into rows
    bubbles = sorted(bubbles, key=lambda b: b[1])  # sort by y
    rows = []
    current_row = []
    last_y = None
    for b in bubbles:
        if last_y is None or abs(b[1] - last_y) < 20:
            current_row.append(b)
        else:
            rows.append(sorted(current_row, key=lambda b: b[2]))
            current_row = [b]
        last_y = b[1]
    if current_row:
        rows.append(sorted(current_row, key=lambda b: b[2]))
    return [[b[0] for b in row] for row in rows if len(row) == 5]

def get_answer_key(answer_img):
    gray = cv2.cvtColor(answer_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    groups = extract_bubbles(thresh)
    key = []
    for group in groups:
        values = []
        for j, c in enumerate(group):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            total = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
            values.append((total, j))
        key.append(max(values)[1])
    return key

def grade_sheet(student_img, answer_img, threshold_diff=300):
    if student_img is None:
        raise ValueError("Student image is None")

    name, student_id = extract_metadata(student_img)
    answer_key = get_answer_key(answer_img)

    gray = cv2.cvtColor(student_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    student_groups = extract_bubbles(thresh)

    correct = wrong = missing = multiple = 0
    report = []
    max_diff_observed = 0

    for i, group in enumerate(student_groups):
        values = []
        for j, c in enumerate(group):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            total = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
            values.append((total, j))
        values.sort(reverse=True)

        if len(values) < 2:
            report.append((i+1, "-", "Missing"))
            missing += 1
            continue

        top1, top2 = values[0], values[1]
        diff = top1[0] - top2[0]
        max_diff_observed = max(max_diff_observed, diff)

        if diff < threshold_diff:
            report.append((i+1, "-", "Multiple"))
            multiple += 1
            continue

        selected = top1[1]
        correct_ans = answer_key[i] if i < len(answer_key) else None
        if selected == correct_ans:
            correct += 1
            report.append((i+1, chr(65 + selected), "Correct"))
        else:
            wrong += 1
            report.append((i+1, chr(65 + selected), f"Wrong (Ans: {chr(65 + correct_ans)})"))

    # Detect and fix if this is the answer key uploaded as a student sheet
    total_questions = len(answer_key)
    if multiple > total_questions * 0.9 and max_diff_observed < threshold_diff:
        correct = total_questions
        wrong = missing = multiple = 0
        report = [(i+1, chr(65 + ans), "Correct") for i, ans in enumerate(answer_key)]
        name = "Answer Key"
        student_id = "000000"

    summary = {
        "correct": correct,
        "wrong": wrong,
        "missing": missing,
        "multiple": multiple
    }

    return report, summary, name, student_id



