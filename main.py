import os
import sys
project_root = os.path.dirname(os.path.abspath(__file__))
ocrlib_path = os.path.join(project_root, 'chineseocr_lite/')
sys.path.append(ocrlib_path)

import argparse
import cv2
import numpy
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
for img in images:
    input = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
    result = ocr.text_predict(input, short_size=960)
    print(result)
