#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/opencv.hpp>
#include <vector>
#include "Video.hpp"

class Color {
public:
    Color(const std::string& name, std::size_t size, double min_area = 100.0);

    void select(Video& video, const std::string& config_file);
    const std::vector<cv::Point>& find_centroid(Video& video);
    bool found();

private:
    static void click_event(int event, int x, int y, int flags, void* userdata);

    std::string name_;
    std::size_t size_;
    double min_area_;
    cv::Scalar lowerb_;
    cv::Scalar upperb_;
    std::vector<cv::Point> centroids_;
};

#endif // COLOR_HPP
