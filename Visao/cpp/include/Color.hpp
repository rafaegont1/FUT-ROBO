#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/opencv.hpp>
#include <vector>
#include "Video.hpp"

class Color {
public:
    Color(const std::string& name);

    void select(Video& video, const std::string& config_file);
    const std::vector<cv::Point> find_centroids(const cv::Mat& frame_hsv, double min_area = 100.0, std::size_t size = 1);
    const std::string& name();
    bool file_lodead();

private:
    static void click_event(int event, int x, int y, int flags, void* userdata);

    std::string name_;
    cv::Scalar lowerb_;
    cv::Scalar upperb_;
    bool file_loaded_ = false;
};

#endif // COLOR_HPP
