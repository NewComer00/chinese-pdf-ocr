[![zh](https://img.shields.io/badge/README-zh-red.svg)](./README.md)
[![en](https://img.shields.io/badge/README-en-gre.svg)](./README.en.md)

# chinese-pdf-ocr
OCR for Chinese PDF file using the API from [DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite).  
> <img src="assets/demo.png" alt="assets/demo.png" width="40%" height="40%">
> <img src="assets/demo_web.png" alt="assets/demo_web.png" width="40%" height="40%">

## Environment
Python >= 3.8

### Tested environment
- x64 Windows 11
  - Python 3.8.0
  - Python 3.11.3
- x64 Ubuntu 22.04.2
  - Python 3.10.12

## Project directory structure
- ```chineseocr_lite/```  
Forked from the lightweight Chinese OCR model implemented by [DayBreak-u/chineseocr\_lite](https://github.com/DayBreak-u/chineseocr_lite).
- ```pdfocr.py```  
The core logic of OCR on PDF files. First perform OCR on a certain page of the PDF, use a graphics algorithm to divide the PDF page into paragraphs based on the recognition results, and finally combine the OCR results by paragraphs.
- ```requirements.txt```  
The Python packages required by ```chineseocr_lite/``` and ```pdfocr.py```.
- ```demo_gui/```  
A simple demo program. Perform OCR on several pages of a given PDF, then output the results to the terminal, and visualize the OCR results of the current page in a new window.
- ```demo_web/```  
A web application that runs on a browser. You can open the PDF on the web page for OCR, and click the recognition result to copy the OCR text to the clipboard.

## Install basic dependencies
The ```requirements.txt``` in the project directory records the Python packages required by ```chineseocr_lite/``` and ```pdfocr.py```. Execute the following command to install:
```
pip3 install -r requirements.txt
```

## Run demo_gui
### Change directory
```
cd demo_gui/
```

### Install poppler
Poppler is needed by Python package [pdf2image](https://github.com/Belval/pdf2image) to transform PDF page into image. [Ways to install](https://github.com/Belval/pdf2image#windows).

### Install additional dependencies
```demo_gui/requirements.txt``` documents the additional Python packages required by ```demo_gui/```. Execute the following command to install:
```
pip3 install -r requirements.txt
```

### Run the main program
```shell
python3 main.py --file <path_to_PDF_file> --start <OCR_start_page> --end <OCR_end_page> [--text-only]
```

> **📘 Example**
> 
> View help information
> ```shell
> python3 main.py -h
> ```
> 
> Perform OCR on the `1.pdf` file in the current directory, starting from page `150` to page `155`. Print the recognized text to the terminal and display the results as images.
> ```shell
> python3 main.py --file ./1.pdf --start 150 --end 155
> ```
> 
> Only print the recognized text to the terminal, without displaying the result images.
> ```shell
> python3 main.py --file ./1.pdf --start 150 --end 155 --text-only
> ```

### Demo
Click on the recognized image, and then press any key on the keyboard to recognize the next page.
![demo](assets/demo.png)

## Run demo_web
### Change directory
```
cd demo_web/
```

### Install additional dependencies
This example uses the Flask package to write the Python web backend.
```
pip3 install -r requirements.txt
```

### Run the main program
```
python3 main.py
```

### View the webpage
To access the service, enter the following URL in your browser (**no internet connection required**):
```
http://127.0.0.1:5000
```
By default, the service can only be accessed through the ```5000``` port of the local address ```127.0.0.1```. If you need to allow other devices in the LAN to access the webpage or want to specify a different port number, please modify the last line of ```demo_web/main.py``` to:
```
app.run(host='0.0.0.0', port=<port number>)
```
⚠️Note:
This service uses the web server that comes with Flask. This server is for development use only and cannot be used in an actual production environment. If you want to publish the service on the public network, you can refer to my other project (in Chinese) [NJUST_HomeworkCollector](https://github.com/NewComer00/NJUST_HomeworkCollector).

### Demo
After opening the webpage, first click the ```Upload PDF``` button in the upper left corner to upload the PDF file to the local browser. Then click the ```Previous``` or ```Next``` button to switch the PDF page. Finally, click the ```OCR``` button in the upper right corner to perform OCR on the current page. The recognized text will be marked by a red box, click the corresponding box to copy the text. Double click on the page number after ```Page:``` to jump to a specified page.
![web rendering](assets/demo_web.png)
