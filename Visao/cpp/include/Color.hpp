#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/opencv.hpp>
#include "Video.hpp"

class Color {
public:
    Color(const std::string& name, double min_area = 100.0);

    void select(const Video::Frame& frame, const std::string& config_file);
    std::optional<cv::Point> find_centroid(const cv::Mat& frame_hsv);

private:
    static void click_event(int event, int x, int y, int flags, void* userdata);

    std::string name;
    double min_area;
    std::pair<int, int> hs_tolerance;
    cv::Scalar lowerb;
    cv::Scalar upperb;
    std::optional<cv::Point> centroid;
};

#endif // COLOR_HPP
