#ifndef CALIBRATION_HPP
#define CALIBRATION_HPP

#include <opencv2/core.hpp>
#include <vector>
#include "futbot/Video.hpp"

class Calibration {
public:
    void calibrate(Video& video);
    cv::Point uvToXy(const cv::Point& uv) const;

private:
    cv::Mat calculateCoeff(const std::vector<std::vector<int>>& uv_points);
    bool fileRead();
    void fileWrite();

    static const std::array<std::array<int, 2>, 5> XY_POINTS;

    cv::Mat m_cte;
};

#endif // CALIBRATION_HPP
