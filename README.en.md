[![zh](https://img.shields.io/badge/README-zh-red.svg)](./README.md)
[![en](https://img.shields.io/badge/README-en-gre.svg)](./README.en.md)

# chinese-pdf-ocr
OCR for Chinese PDF file using the API from [DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite).

## Usage
### Install poppler
Poppler is needed by Python package [pdf2image](https://github.com/Belval/pdf2image) to transform PDF page into image. [Ways to install](https://github.com/Belval/pdf2image#how-to-install).

### Install Python requirements
```
pip3 install -r requirements.txt
```

### Run the main program
```
python3 main.py --file <PDF file path> --start <start page num> --end <end page num>
```
**📘 Example**  
Do OCR on ```1.pdf``` in current dir from page ```150``` to page ```155```.
```
python3 main.py --file ./1.pdf --start 150 --end 155
```

## Demo
![demo](assets/demo.png)
