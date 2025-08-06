#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/core.hpp>
#include <vector>
#include "futbot/Video.hpp"

class Color {
public:
    Color();
    Color(const std::string& name);

    void select(Video& video, const std::string& configFile);
    std::vector<cv::Point> findCentroids(const cv::Mat& frameHsv,
        double minArea = 100.0, std::size_t size = 1) const;
    void showSelectedColor(const Video& video) const;

    // Getters for member variables
    const std::string& name() const { return m_name; }
    bool fileLodead() const { return m_fileLoaded; }

private:
    void readFile();

    std::string m_name;
    cv::Scalar m_lowerb;
    cv::Scalar m_upperb;
    bool m_fileLoaded = false;
};

#endif // COLOR_HPP
