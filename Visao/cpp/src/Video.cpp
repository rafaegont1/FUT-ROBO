#include "futbot/Video.hpp"

#include <cstdio>
#include <iostream>
#include <stdexcept>
#include <opencv2/imgproc.hpp>

Video::Video(const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        throw std::runtime_error("Couldn't open file " + config_file);
    }

    // cap_.open("../../testes/new/output.avi"); // rascunho
    cap_.open((int)fs["camera"]["id"]);
    cap_.set(cv::CAP_PROP_FRAME_WIDTH, (double)fs["camera"]["width"]);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, (double)fs["camera"]["height"]);
    cap_.set(cv::CAP_PROP_FPS, (double)fs["camera"]["fps"]);

    fs["window"]["name"] >> win_name_;
    fs["window"]["delay"] >> win_delay_;

    cv::namedWindow(win_name_);

    fs.release();
}

Video::~Video()
{
    cap_.release();
    cv::destroyWindow(win_name_);
}

void Video::update()
{
    cap_ >> frame.raw;

    if (frame.raw.empty()) {
        std::cout << "Rewinding video..." << std::endl;
        cap_.set(cv::CAP_PROP_POS_FRAMES, 0);
        cap_ >> frame.raw;
    }

    cv::cvtColor(frame.raw, frame.hsv, cv::COLOR_BGR2HSV);
}

int Video::show()
{
    cv::imshow(win_name_, frame.raw);
    return cv::waitKey(win_delay_);
}

void Video::draw_text(const cv::String& text, const cv::Point& org, const cv::Scalar& color)
{
    cv::putText(frame.raw, text, org, cv::FONT_HERSHEY_PLAIN, 1.5, color, 2);
}

void Video::draw_circle(const cv::Point& center, const cv::String& text)
{
    // const cv::String text = std::to_string(xy.x) + ',' + std::to_string(xy.y);

    cv::circle(frame.raw, center, 3, cv::Scalar(0, 0, 255), 2);
    cv::putText(frame.raw, text, center, cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(0, 0, 0));
}

std::string Video::win_name() const
{
    return win_name_;
}

int Video::win_delay() const
{
    return win_delay_;
}
