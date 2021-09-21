import os
import sys
import random
import argparse

import cv2
import numpy as np
from sklearn.cluster import KMeans
from pdf2image import convert_from_path, convert_from_bytes

project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)

from model import OcrHandle

parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str)
parser.add_argument("--start", type=int)
parser.add_argument("--end", type=int)
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
    word_sizes = np.zeros(len(results))
    left_margins = np.zeros(len(results))
    right_margins = np.zeros(len(results))
    for idx, res in enumerate(results):
        rect = np.int32(res[0])
        line_color = random.choices(range(256), k=3)
        cv2.polylines(output, [rect], isClosed=True, thickness=4, color=line_color)

        word_sizes[idx] = (rect[3][1]-rect[0][1]+rect[2][1]-rect[1][1])/2
        left_margins[idx] = (rect[0][0]+rect[3][0])/2
        right_margins[idx] = (rect[1][0]+rect[2][0])/2

    word_sizes = np.square(word_sizes)
    right_margins = input.shape[1] - right_margins

    word_sizes = word_sizes/np.linalg.norm(word_sizes)
    left_margins = left_margins/np.linalg.norm(left_margins)
    right_margins = right_margins/np.linalg.norm(right_margins)

    features = np.array([word_sizes,left_margins])
    print(features)

    kmeans = KMeans(n_clusters=4, random_state=0).fit(features.T)
    for idx, label in enumerate(kmeans.labels_):
        cv2.putText(output, str(label), results[idx][0][0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)

    window = "Output Page %s" % page
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.imshow(window, output)
    cv2.waitKey(0)
