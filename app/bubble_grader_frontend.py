# omr_digit_grader.py
import cv2
import numpy as np
import os
from imutils.perspective import four_point_transform
from imutils import contours
import imutils

def load_and_preprocess(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)
    return image, gray, edged

def find_document_contour(edged):
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            return approx
    return None

def extract_bubbles(warped_gray):
    thresh = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    question_cnts = []
    for c in cnts:
        (x, y, w, h) = cv2.boundingRect(c)
        aspect_ratio = w / float(h)
        if w >= 20 and h >= 20 and 0.3 <= aspect_ratio <= 1.0:
            question_cnts.append(c)

    question_cnts = contours.sort_contours(question_cnts, method="top-to-bottom")[0]
    return thresh, question_cnts

def grade(thresh, question_cnts, answer_key):
    questions = 30
    choices_per_question = 10  # digits 0–9
    correct = 0
    results = []

    for (q, i) in enumerate(range(0, len(question_cnts), choices_per_question)):
        cnts = contours.sort_contours(question_cnts[i:i + choices_per_question])[0]
        bubbled = None

        for (j, c) in enumerate(cnts):
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)
            total = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)

        result = {
            'question': q + 1,
            'selected': bubbled[1],
            'correct': answer_key.get(q + 1),
            'is_correct': bubbled[1] == answer_key.get(q + 1)
        }
        if result['is_correct']:
            correct += 1
        results.append(result)

    score = (correct / questions) * 100
    return results, score

def parse_answer_key(image_path):
    # Replace this with actual bubble extraction
    # Dummy key for testing: All answers are digit 1
    return {i: 1 for i in range(1, 31)}

def main(answer_key_path, answer_sheets_dir):
    answer_key = parse_answer_key(answer_key_path)

    for filename in os.listdir(answer_sheets_dir):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        image_path = os.path.join(answer_sheets_dir, filename)
        image, gray, edged = load_and_preprocess(image_path)
        doc_cnt = find_document_contour(edged)
        if doc_cnt is None:
            print(f"Could not find document boundary in {filename}")
            continue

        warped = four_point_transform(image, doc_cnt.reshape(4, 2))
        warped_gray = four_point_transform(gray, doc_cnt.reshape(4, 2))

        thresh, question_cnts = extract_bubbles(warped_gray)
        results, score = grade(thresh, question_cnts, answer_key)

        print(f"\nResult for {filename}:")
        for res in results:
            print(f"Q{res['question']:02d}: Selected {res['selected']} | Correct: {res['correct']} | {'✅' if res['is_correct'] else '❌'}")
        print(f"Final Score: {score:.2f}%")

if __name__ == "__main__":
    # Update these paths
    answer_key_image = "answer_sheets/20250529110230_014.jpg"
    student_answer_dir = "answer_sheets/"
    main(answer_key_image, student_answer_dir)



