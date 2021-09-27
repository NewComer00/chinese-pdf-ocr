import argparse
import os
import random
import sys

import cv2
import numpy as np
from pdf2image import convert_from_path, convert_from_bytes

project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)

from model import OcrHandle

parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True)
parser.add_argument("--start", type=int, required=True)
parser.add_argument("--end", type=int, required=True)
args = parser.parse_args()

pdf_path = args.file
start_page = args.start
end_page = args.end

ocr = OcrHandle()
images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
for idx, img in enumerate(images):
    page = start_page + idx

    input = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    results = ocr.text_predict(input, short_size=960)

    output = np.array(input, copy=True)
    line_heights = np.zeros(len(results))
    box_centers = np.zeros((len(results), 2))
    for idx, res in enumerate(results):
        rect = np.int32(res[0])
        box_centers[idx] = np.mean(rect, axis=0)
        line_heights[idx] = (rect[3][1] - rect[0][1] + rect[2][1] - rect[1][1]) / 2

        # draw the OCR result boxes
        line_color = random.choices(range(256), k=3)
        cv2.polylines(output, [rect], isClosed=True, thickness=2, color=line_color)

    # get the contours of text contents using computer graphics algorithms
    line_ht_avg = round(np.mean(line_heights))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (line_ht_avg, line_ht_avg))
    half_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (line_ht_avg // 2, line_ht_avg // 2))

    gray = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blur, 255 // 2, 255, cv2.THRESH_BINARY)
    inverse = cv2.bitwise_not(binary)

    dilate = cv2.dilate(inverse, kernel)
    morph_close = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, half_kernel)
    contours, hierarchy = cv2.findContours(morph_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # classify the OCR results by their positions
    labels = -np.ones(len(results), dtype=int)
    for cont_idx, cont in enumerate(contours):
        for label_idx in range(len(labels)):
            # if the center of a OCR result box is inside some contour ...
            if cv2.pointPolygonTest(cont, tuple(box_centers[label_idx]), False) >= 0:
                labels[label_idx] = cont_idx

    # draw contours and labels of all results
    cv2.drawContours(output, contours, -1, (0, 0, 255), 3, cv2.LINE_AA)
    for idx, label in enumerate(labels):
        cv2.putText(output, str(label), results[idx][0][0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)

    window = "Output Page %s" % page
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.imshow(window, output)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
