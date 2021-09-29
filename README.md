# chinese-pdf-ocr
OCR for Chinese PDF file using api from DayBreak-u/chineseocr\_lite

## Usage
```
pip3 install -r requirements.txt
python3 main.py --file <path of your PDF file> --start <page number to start OCR> --end <page number to end OCR>
```

📘Example:  
Do OCR on ```1.pdf``` in current dir from page ```150``` to ```155```.
```
python3 main.py --file ./1.pdf --start 150 --end 155
```

## Demo
![demo](assets/demo.png)
