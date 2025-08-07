#ifndef VIDEO_HPP
#define VIDEO_HPP

#include <opencv2/highgui.hpp>
#include <string>

class Video {
public:
    Video(const std::string& configFile);
    virtual ~Video();

    void updateFrame();
    int showFrame();
    void putText(const cv::String& text, const cv::Point& org = cv::Point(0, 20),
        const cv::Scalar& color = cv::Scalar(80, 80, 80));
    void drawCircle(const cv::Point& center, int radius);
    void drawRect(const cv::Rect& rect);

    // Member variables getters
    const std::string& windowName() const { return m_windowName; }
    int windowDelay() const { return m_windowDelay; }
    const cv::Mat& frame() const { return m_frame; };
    const cv::Mat& frameHsv() const { return m_frameHsv; };

private:
    cv::VideoCapture m_cap;
    cv::Mat m_frame;
    cv::Mat m_frameHsv;
    std::string m_windowName;
    int m_windowDelay;
};

#endif // VIDEO_HPP
