import os
import sys
import random
import argparse

import cv2
import numpy as np
from pdf2image import convert_from_path

# self-defined modules to be added to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__)) + '/..'
sys.path.append(project_root)
from pdfocr import PdfOcrTool
# end of self-defined module list


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    args = parser.parse_args()

    return args.file, args.start, args.end


def main():
    pdf_path, start_page, end_page = get_args()

    # init pdf ocr tool
    ocr = PdfOcrTool(newline="\n")

    # read in pdf pages and transform them to images
    print("Loading page(s) from PDF file...")
    images = convert_from_path(pdf_path,
                               first_page=start_page,
                               last_page=end_page)
    for img_idx, img in enumerate(images):
        page_num = start_page + img_idx
        print("Processing page %s ..." % page_num)

        # do OCR for the input page image
        page_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        labeled_textbox = ocr.predict(page_img)

        # visualize the OCR and clustering result
        for label, textbox in labeled_textbox.items():
            print("<%s>\n%s" % (label, textbox[1]))
            label_color = random.choices(range(256), k=3)
            x, y, w, h = textbox[0]
            cv2.rectangle(page_img, (x, y), (x + w, y + h), label_color, 3)
            cv2.putText(page_img, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        label_color, 4, cv2.LINE_AA)

        window = "Output Page %s" % page_num
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.imshow(window, page_img)
        cv2.waitKey(0)


if __name__ == "__main__":
    main()
