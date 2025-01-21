#ifndef VIDEO_HPP
#define VIDEO_HPP

#include <opencv2/opencv.hpp>
#include <string>

class Video {
public:
    struct Frame {
        cv::Mat raw;
        cv::Mat hsv;
    };

    Video(const std::string& config_file);
    virtual ~Video();

    void update();
    int show();
    void draw_text(
        const cv::String& text,
        const cv::Point& org = cv::Point(0, 20),
        const cv::Scalar& color = cv::Scalar(80, 80, 80)
    );
    void draw_circle(const cv::Point& center, const cv::String& text);

    std::string win_name() const;
    int win_delay() const;

    Frame frame;

private:
    cv::VideoCapture cap_;
    std::string win_name_;
    int win_delay_;
};

#endif // VIDEO_HPP
