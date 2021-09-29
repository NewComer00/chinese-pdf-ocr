[![zh](https://img.shields.io/badge/README-zh-red.svg)](./README.md)
[![en](https://img.shields.io/badge/README-en-gre.svg)](./README.en.md)

# chinese-pdf-ocr
对中文PDF文件进行OCR。使用了[DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite)的OCR模型。

## 用法
### 安装poppler
用于PDF转图片，被Python的[pdf2image](https://github.com/Belval/pdf2image)包使用。各平台的[安装方法](https://github.com/Belval/pdf2image#windows)。

### 安装Python依赖包
```
pip3 install -r requirements.txt
```

### 运行主程序
```
python3 main.py --file <PDF文件路径> --start <OCR开始页码> --end <OCR结束页码>
```
**📘 示例**  
对当前目录下的```1.pdf```文件进行OCR，页码从```150```开始，到```155```结束。
```
python3 main.py --file ./1.pdf --start 150 --end 155
```

## 效果图
![效果图](assets/demo.png)
