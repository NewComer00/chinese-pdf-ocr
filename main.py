import argparse
import os
import random
import sys

import cv2
import numpy as np
import onnxruntime as ort
from pdf2image import convert_from_path

# self-defined modules to be added th PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)

from model import OcrHandle

# end of self-defined module list

# presetting of the modules
ort.set_default_logger_severity(3)  # turn off onnxruntime warnings


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    args = parser.parse_args()

    return args.file, args.start, args.end


def classify_text(page_img, ocr_results):
    output = np.array(page_img, copy=True)
    line_heights = np.zeros(len(ocr_results))
    box_centers = np.zeros((len(ocr_results), 2))
    for idx, res in enumerate(ocr_results):
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

    gray = cv2.cvtColor(page_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blur, 255 // 2, 255, cv2.THRESH_BINARY)
    inverse = cv2.bitwise_not(binary)

    dilate = cv2.dilate(inverse, kernel)
    morph_close = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, half_kernel)
    contours, hierarchy = cv2.findContours(morph_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # classify the OCR results by their positions
    labels = -np.ones(len(ocr_results), dtype=int)
    for cont_idx, cont in enumerate(contours):
        for res_idx, res in enumerate(ocr_results):
            # if the center of a OCR result box is inside some contour ...
            if cv2.pointPolygonTest(cont, tuple(box_centers[res_idx]), False) >= 0:
                labels[res_idx] = cont_idx

    # draw contours and labels of all results
    # cv2.drawContours(output, contours, -1, (0, 0, 255), 3, cv2.LINE_AA)
    return labels


def main():
    pdf_path, start_page, end_page = get_args()

    ocr = OcrHandle()
    images = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    for img_idx, img in enumerate(images):
        page_num = start_page + img_idx
        print("Processing page %s ..." % page_num)

        page_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        ocr_results = ocr.text_predict(page_img, short_size=960)
        ocr_results = np.array(ocr_results, dtype=object)

        labels = classify_text(page_img, ocr_results)

        results_with_label = []
        for label_name in np.unique(labels):
            indices = np.where(labels == label_name)
            results_with_label.append((label_name, ocr_results[indices]))

        for results_in_class in results_with_label:
            print("\n" + "=" * 80)
            print("Text in block %d:" % results_in_class[0])
            for text_line in results_in_class[1][:, 1]:
                print(text_line[4:])
            print("=" * 80 + "\n")

            points = np.vstack(results_in_class[1][:, 0]).astype(int)
            x, y, w, h = cv2.boundingRect(points)
            cv2.rectangle(page_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
            cv2.putText(page_img, str(results_in_class[0]), (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)

        window = "Output Page %s" % page_num
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window, page_img)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('n'):
                break


if __name__ == "__main__":
    main()
