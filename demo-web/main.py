import os
import sys
import base64
import json
import cv2
import numpy as np
from flask import Flask, render_template, redirect, url_for, request, make_response

# self-defined modules to be added th PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__)) + '/..'
sys.path.append(project_root)
from pdfocr import PdfOcrTool
# end of self-defined module list

app = Flask(__name__)
ocr = PdfOcrTool()


# the minimal Flask application
@app.route('/', methods=['GET', 'POST'])
def index():
    # get the image of the current pdf page
    # perform ocr on the image and return the result
    if request.method == 'POST':
        datafromjs = request.form['page_img']
        encoded_data = datafromjs.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        page_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        labeled_textbox = ocr.predict(page_img)
        response = make_response(json.dumps(labeled_textbox))
        response.headers['Content-Type'] = "application/json"
        return response
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
