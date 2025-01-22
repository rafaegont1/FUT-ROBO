#ifndef CALIBRATION_HPP
#define CALIBRATION_HPP

#include <opencv2/core.hpp>
#include <vector>
#include "futbot/Video.hpp"

class Calibration {
public:
    void calibrate(Video& video);
    cv::Point uv_to_xy(const cv::Point& uv) const;

private:
    static void click_event(int event, int x, int y, int, void* param);
    cv::Mat coef_calc(const std::vector<std::vector<int>>& uv_points);
    bool file_read();
    void file_write();

    static const std::array<std::array<int, 2>, 5> XY_POINTS;

    cv::Mat cte_;
}; // namespace Calibration

#endif // CALIBRATION_HPP
