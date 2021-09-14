import cv2
import numpy
from model import OcrHandle
from pdf2image import convert_from_path, convert_from_bytes

pdf_path = '/mnt/d/Desktop/1.pdf'
images = convert_from_path(pdf_path, first_page=10, last_page=10)
input = cv2.cvtColor(numpy.array(images[0]), cv2.COLOR_RGB2BGR)

ocr = OcrHandle()
result = ocr.text_predict(input, short_size=960)

print(result)
