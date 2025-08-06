#ifndef BALL_HPP
#define BALL_HPP

#include "futbot/Color.hpp"
#include "futbot/Calibration.hpp"
// #include "futbot/Publisher.hpp"

class Ball {
public:
    Ball(const Calibration& calib);
    Ball(const Color& color, const Calibration& calib, const std::string& configFile);
    const cv::Point& findPose(Video& video);
    // void publish_pose(Publisher& publisher);
    const cv::Point& centroidWorld() const;
    // std::string centroid_msg() const;

private:
    void fileRead(const std::string& configFile);

    Color m_color;
    cv::Point m_centroidImage;
    cv::Point m_centroidWorld;
    double m_minArea;
    Calibration m_calib;
    bool m_found = false;
};

#endif // BALL_HPP
