import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)

import argparse
import random
import cv2
import numpy as np
from model import OcrHandle
from pdf2image import convert_from_path, convert_from_bytes

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
    print(results)

    output = np.array(input, copy=True)
    for res in results:
        rect = np.int32([res[0]])
        line_color = random.choices(range(256), k=3)
        cv2.polylines(output, rect, isClosed=True, thickness=4, color=line_color)
    
    window = "Output Page %s" % page
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)
    cv2.imshow(window, output)
    cv2.waitKey(0)
