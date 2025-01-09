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

    Frame frame;

private:
    cv::VideoCapture cap_;
    std::string win_name_;
    int win_delay_;
};

#endif // VIDEO_HPP
