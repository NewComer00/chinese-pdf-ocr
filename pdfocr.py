import argparse
import os
import random
import re
import sys

import cv2
import numpy as np
import onnxruntime as ort
from pdf2image import convert_from_path

# self-defined modules to be added to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)
from model import OcrHandle
# end of self-defined module list

# presetting of the modules
ort.set_default_logger_severity(3)  # turn off onnxruntime warnings


class PdfOcrTool:

    def __init__(self):
        print("Initializing OCR model...")
        self.ocr_model = OcrHandle()

    # input
    # page_img: cv2 BGR image
    # output
    # labeled_textbox:
    # { label_name: (bounding box, text) }
    def predict(self, page_img):
        print("Performing OCR on page ...")
        # do OCR for the input page image
        ocr_results = self.ocr_model.text_predict(page_img, short_size=960)

        # do clustering on the ocr result
        ocr_results = np.array(ocr_results, dtype=object)
        labeled_results = self._text_cluster(page_img, ocr_results)

        # group the textbox by their labels
        labeled_textbox = self._get_labeled_textbox(labeled_results)
        print("Done.")
        return labeled_textbox

    def _text_cluster(self, page_img, ocr_results):
        line_heights = np.zeros(len(ocr_results))
        box_centers = np.zeros((len(ocr_results), 2))
        for idx, res in enumerate(ocr_results):
            rect = np.int32(res[0])
            box_centers[idx] = np.mean(rect, axis=0)
            line_heights[idx] = (rect[3][1] - rect[0][1] + rect[2][1] -
                                 rect[1][1]) / 2

        # get the contours of text contents using computer graphics algorithms
        line_ht_avg = round(np.mean(line_heights))
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT,
                                           (line_ht_avg, line_ht_avg))
        half_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (line_ht_avg // 2, line_ht_avg // 2))

        gray = cv2.cvtColor(page_img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blur, 255 // 2, 255, cv2.THRESH_BINARY)
        inverse = cv2.bitwise_not(binary)

        dilate = cv2.dilate(inverse, kernel)
        morph_close = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, half_kernel)
        contours, hierarchy = cv2.findContours(morph_close, cv2.RETR_EXTERNAL,
                                               cv2.CHAIN_APPROX_SIMPLE)

        # do OCR results clustering by their positions
        labels = -np.ones(len(ocr_results), dtype=int)
        contours.reverse(
        )  # from the upper parts of the page to the lower parts
        for cont_idx, cont in enumerate(contours):
            for res_idx, res in enumerate(ocr_results):
                # if the center of a OCR result box is inside some contour ...
                if cv2.pointPolygonTest(cont, tuple(box_centers[res_idx]),
                                        False) >= 0:
                    labels[res_idx] = cont_idx

        labeled_results = {}
        for label_name in np.unique(labels):
            indices = np.where(labels == label_name)
            labeled_results[str(label_name)] = ocr_results[indices]
        return labeled_results

    # output: labeled_textbox
    # { label_name: (bounding box, text) }
    def _get_labeled_textbox(self, labeled_results):
        labeled_textbox = {}
        for label_name, result in labeled_results.items():
            # get the bounding box of text with the same label
            points = np.vstack(result[:, 0]).astype(int)
            bounding_box = cv2.boundingRect(points)
            # concat the text with the same label
            text = ""
            for text_line in result[:, 1]:
                text += re.sub(r"^(\d+、\s)", "", text_line)
                text += "\n"

            labeled_textbox[label_name] = (bounding_box, text)
        return labeled_textbox
