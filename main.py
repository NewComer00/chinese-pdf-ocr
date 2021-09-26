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
    line_heights = np.zeros(len(results))
    line_centers = np.zeros(len(results))
    for idx, res in enumerate(results):
        rect = np.int32(res[0])
        line_color = random.choices(range(256), k=3)
        cv2.polylines(output, [rect], isClosed=True, thickness=4, color=line_color)

        line_heights[idx] = (rect[3][1]-rect[0][1]+rect[2][1]-rect[1][1])/2
        line_centers[idx] = (rect[0][0]+rect[3][0]+rect[1][0]+rect[2][0])/4
    
    # get text blocks
    line_ht_avg = round(np.mean(line_heights))
    kernel = np.ones((line_ht_avg,line_ht_avg), np.uint8)
    input = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
    input = cv2.GaussianBlur(input,(5,5),0)
    _,input = cv2.threshold(input,255//3,255,cv2.THRESH_BINARY)
    input = cv2.erode(input, kernel)
    input = cv2.morphologyEx(input, cv2.MORPH_OPEN, kernel)

    word_sizes = np.square(line_heights)
    word_sizes = word_sizes/np.linalg.norm(word_sizes)
    line_centers = line_centers/np.linalg.norm(line_centers)
    features = np.array([word_sizes,line_centers])

    kmeans = KMeans(n_clusters=4, random_state=0).fit(features.T)
    print(np.unique(kmeans.labels_, return_counts=True))

    for idx, label in enumerate(kmeans.labels_):
        cv2.putText(output, str(label), results[idx][0][0], cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3, cv2.LINE_AA)

    window = "Output Page %s" % page
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.imshow(window, input)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
