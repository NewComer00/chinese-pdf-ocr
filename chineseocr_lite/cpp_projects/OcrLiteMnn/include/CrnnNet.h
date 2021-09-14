#ifndef __OCR_CRNNNET_H__
#define __OCR_CRNNNET_H__

#include "OcrStruct.h"
#include <opencv2/opencv.hpp>
#include <Interpreter.hpp>

class CrnnNet {
public:

    CrnnNet();
    ~CrnnNet();
    void setNumThread(int numOfThread);

    void initModel(const std::string &pathStr, const std::string &keysPath);

    std::vector<TextLine> getTextLines(std::vector<cv::Mat> &partImg, const char *path, const char *imgName);

private:
    std::shared_ptr<MNN::Interpreter> net;
    MNN::Session* session;  
    bool isOutputDebugImg = false;
    int numThread = 4;

    const float meanValues[3] = {127.5, 127.5, 127.5};
    const float normValues[3] = {1.0 / 127.5, 1.0 / 127.5, 1.0 / 127.5};
    const int dstHeight = 32;

    std::vector<std::string> keys;

    TextLine scoreToTextLine(const std::vector<float> &outputData, int h, int w);

    TextLine getTextLine(const cv::Mat &src);
};


#endif //__OCR_CRNNNET_H__
