#include "Video.hpp"
#include <cstdio>
#include <iostream>
#include <stdexcept>

Video::Video(const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        throw std::runtime_error("Couldn't open file " + config_file);
    }

    cap_.open("../../testes/new/output.avi"); // rascunho
    // cap_.open((int)fs["camera"]["id"]);
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
