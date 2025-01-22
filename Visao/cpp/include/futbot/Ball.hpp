#ifndef BALL_HPP
#define BALL_HPP

#include "futbot/Color.hpp"
#include "futbot/Calibration.hpp"

class Ball {
public:
    Ball(const Color& color, const Calibration& calib);
    const cv::Point& find_pose(Video& video);
    const cv::Point& centroid_world() const;
    std::string centroid_msg() const;

private:
    void file_read(const std::string& config_file = "../config.yaml");

    Color color_;
    cv::Point centroid_image_;
    cv::Point centroid_world_;
    double min_area_;
    Calibration calib_;
    bool found_ = false;
};

#endif // BALL_HPP
