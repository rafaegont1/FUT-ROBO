#ifndef BALL_HPP
#define BALL_HPP

#include <opencv2/core.hpp>
#include "futbot/Video.hpp"

class Ball {
public:
    Ball();
    virtual ~Ball();

    void selectColor(Video& video);
    void showSelectedColor(const Video& video) const;
    std::optional<std::tuple<cv::Point2f, float>> findCentroid(
        const cv::Mat& frame) const;

    // Member variable getters
    const cv::Scalar& lowerb() const { return m_lowerb; };
    const cv::Scalar& upperb() const { return m_upperb; };

private:
    cv::Scalar m_lowerb;
    cv::Scalar m_upperb;
};

#endif // BALL_HPP
