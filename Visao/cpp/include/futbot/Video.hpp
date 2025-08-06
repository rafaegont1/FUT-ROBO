#ifndef VIDEO_HPP
#define VIDEO_HPP

#include <opencv2/highgui.hpp>
#include <string>

class Video {
public:
    struct Frame {
        cv::Mat raw;
        cv::Mat hsv;
    };

    Video(const std::string& config_file);
    virtual ~Video();

    void updateFrame();
    int showFrame();
    void putText(const cv::String& text, const cv::Point& org = cv::Point(0, 20),
        const cv::Scalar& color = cv::Scalar(80, 80, 80));
    void drawCircle(const cv::Point& center, const cv::String& text);
    void drawRect(const cv::Rect& rect);

    std::string windowName() const { return m_windowName; }
    int windowDelay() const { return m_windowDelay; }

    Frame frame;

private:
    cv::VideoCapture m_cap;
    std::string m_windowName;
    int m_windowDelay;
};

#endif // VIDEO_HPP
