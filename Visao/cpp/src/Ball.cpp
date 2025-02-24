#include "futbot/Ball.hpp"

Ball::Ball(const Color& color, const Calibration& calib)
: color_{color}, calib_{calib}
{
    file_read();
}

const cv::Point& Ball::find_pose(Video& video)
{
    std::vector<cv::Point> centroids =
        color_.find_centroids(video.frame.hsv, min_area_);

    if (centroids.empty()) {
        found_ = false;
    } else {
        centroid_image_ = centroids[0];
        centroid_world_ = calib_.uv_to_xy(centroids[0]);
        const std::string circle_text = "BALL: " +
            std::to_string(centroid_world_.x) + ',' +
            std::to_string(centroid_world_.y) + ',';
        video.draw_circle(centroid_image_, circle_text);
        found_ = true;
    }

    return centroid_world_;
}

void Ball::publish_pose(Publisher& publisher)
{
    const std::string pub_msg =
        std::to_string(centroid_world_.x) + ',' +
        std::to_string(centroid_world_.y) + ',';
    const std::string pub_topic = "BALL";

    publisher.publish(pub_msg, pub_topic);
}

const cv::Point& Ball::centroid_world() const
{
    return centroid_world_;
}

void Ball::file_read(const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        throw std::runtime_error("Couldn't open file " + config_file);
    }

    fs["color"]["ball_min_area"] >> min_area_;

    fs.release();
}

// std::string Ball::centroid_msg() const
// {
//     return std::to_string(centroid_world_.x) + ',' +
//            std::to_string(centroid_world_.x) + ',';
// }
