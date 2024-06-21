[![zh](https://img.shields.io/badge/README-zh-red.svg)](./README.md)
[![en](https://img.shields.io/badge/README-en-gre.svg)](./README.en.md)

# chinese-pdf-ocr
对中文PDF文件进行OCR。使用了[DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite)的OCR模型。  
> <img src="assets/demo.png" alt="assets/demo.png" width="40%" height="40%">
> <img src="assets/demo_web.png" alt="assets/demo_web.png" width="40%" height="40%">

## 环境要求
Python >= 3.8

### 测试环境
- x64 Windows 11
  - Python 3.8.0
  - Python 3.11.3
- x64 Ubuntu 22.04.2
  - Python 3.10.12

## 项目目录结构
- ```chineseocr_lite/```  
引用自[DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite)实现的轻量级中文OCR模型。
- ```pdfocr.py```  
对PDF文件进行OCR的核心逻辑。先对PDF某一页进行OCR，基于识别结果使用图形学算法对PDF该页划分段落，最后把OCR结果按段落组合。
- ```requirements.txt```  
记录了```chineseocr_lite/```和```pdfocr.py```所需要的Python包。
- ```demo_gui/```  
一个简单的小程序。对给定的PDF的若干页进行OCR，然后将结果输出至终端，并在新的窗口中可视化显示当前页面的OCR结果。
- ```demo_web/```  
在浏览器上运行的网页应用。可以在网页上打开PDF进行OCR，鼠标点击识别结果可以将OCR文字复制到剪贴板。

## 安装基础依赖包
项目目录下的```requirements.txt```  记录了```chineseocr_lite/```和```pdfocr.py```所需要的Python包。执行以下命令来安装：
```
pip3 install -r requirements.txt
```

## 运行demo_gui
### 切换目录
```
cd demo_gui/
```

### 安装poppler
用于PDF转图片，被Python的[pdf2image](https://github.com/Belval/pdf2image)包使用。各平台的[安装方法](https://github.com/Belval/pdf2image#windows)。

### 安装额外的依赖包
```demo_gui/requirements.txt```  记录了```demo_gui/```所需要的额外Python包。执行以下命令来安装：
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

### 效果图
点击识别后的图片，然后按键盘上任意键即可识别下一页。
![效果图](assets/demo.png)

## 运行demo_web
### 切换目录
```
cd demo_web/
```

### 安装额外的依赖包
本示例使用了Flask包来编写Python网页后端。
```
pip3 install -r requirements.txt
```

### 运行主程序
```
python3 main.py
```

### 访问网页
要访问该服务，在浏览器中输入如下网址（**无需互联网连接**）：
```
http://127.0.0.1:5000
```
默认情况下，该服务只能通过本机地址```127.0.0.1```的```5000```端口访问。如果需要让局域网内的其它设备也能访问该网页，或是需要不同的端口号，请将```demo_web/main.py```的最后一行修改为：
```
app.run(host='0.0.0.0', port=<端口号>)
```
⚠️注意：  
本服务使用了Flask自带的网页服务器。该服务器仅供开发使用，不能在实际生产环境中使用。如需将服务发布在公网，可以参考我的另一个项目[NJUST_HomeworkCollector](https://github.com/NewComer00/NJUST_HomeworkCollector)。

### 效果图
打开网页后，先点击左上角的```Upload PDF```按钮上传PDF文件到本机浏览器。然后点击```Previous```或```Next```按钮切换PDF上/下页。最后点击右上角的```OCR```按钮，对当前页进行OCR。识别到的文本会由红框标出，点击对应的方框即可复制其中的文字。双击```Page:```后的当前页码，可以编辑并跳转到指定页。
![web效果图](assets/demo_web.png)
