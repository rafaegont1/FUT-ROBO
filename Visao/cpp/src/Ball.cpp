#include "futbot/Ball.hpp"

Ball::Ball(const Calibration& calib) : m_calib{calib}
{
}

Ball::Ball(const Color& color, const Calibration& calib, const std::string& configFile)
    : m_color{color}, m_calib{calib}
{
    fileRead(configFile);
}

const cv::Point& Ball::findPose(Video& video)
{
    std::vector<cv::Point> centroids =
        m_color.findCentroids(video.frame.hsv, m_minArea);

    if (centroids.empty()) {
        m_found = false;
    } else {
        m_centroidImage = centroids[0];
        m_centroidWorld = m_calib.uvToXy(centroids[0]);
        auto circleText = std::format("BALL: {},{},", m_centroidWorld.x, m_centroidWorld.y);
        video.drawCircle(m_centroidImage, circleText);
        m_found = true;
    }

    return m_centroidWorld;
}

// void Ball::publish_pose(Publisher& publisher)
// {
//     const std::string pub_msg =
//         std::to_string(centroid_world_.x) + ',' +
//         std::to_string(centroid_world_.y) + ',';
//     const std::string pub_topic = "BALL";

//     publisher.publish(pub_msg, pub_topic);
// }

const cv::Point& Ball::centroidWorld() const
{
    return m_centroidWorld;
}

void Ball::fileRead(const std::string& configFile)
{
    cv::FileStorage fs(configFile, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        throw std::runtime_error(std::format("Couldn't open file {}", configFile));
    }

    fs["color"]["ballMinArea"] >> m_minArea;

    fs.release();
}

// std::string Ball::centroid_msg() const
// {
//     return std::to_string(centroid_world_.x) + ',' +
//            std::to_string(centroid_world_.x) + ',';
// }
