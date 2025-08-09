#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/core.hpp>
#include <vector>
#include "futbot/Video.hpp"

class Color {
public:
    inline static auto BLACK = cv::Scalar(0, 0, 0);
    inline static auto WHITE = cv::Scalar(255, 255, 255);
    inline static auto BLUE = cv::Scalar(255, 0, 0);
    inline static auto GREEN = cv::Scalar(0, 255, 0);
    inline static auto RED = cv::Scalar(0, 0, 255);
    inline static auto YELLOW = cv::Scalar(0, 255, 255);
    inline static auto CYAN = cv::Scalar(255, 255, 0);
    inline static auto PINK = cv::Scalar(255, 0, 255);

    Color();
    Color(const std::string& name);

    bool readFile(const std::string& filename);
    bool writeFile(const std::string& filename);
    void select(Video& video);
    void showSelection(const Video& video) const;
    void findContours(const cv::Mat& frameHsv,
        std::vector<std::vector<cv::Point>> &contours) const;
    std::vector<std::vector<cv::Point>> findNLargestContours(
        const cv::Mat& frameHsv, int n) const;
    std::vector<cv::Point> findLargestContour(const cv::Mat& frameHsv) const;

    // Getters for member variables
    const std::string& name() const { return m_name; }
    const cv::Scalar& lowerb() const { return m_lowerb; }
    const cv::Scalar& upperb() const { return m_upperb; }

private:
    std::string m_name;
    cv::Scalar m_lowerb;
    cv::Scalar m_upperb;
};

#endif // COLOR_HPP
