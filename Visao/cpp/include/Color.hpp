#ifndef COLOR_HPP
#define COLOR_HPP

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <tuple>
#include <optional>

class Color {
public:
    struct Pose {
        int u;
        int v;
    };

    // Constructor
    Color(
        const std::string& name,
        int min_area = 100,
        std::tuple<int, int> hs_tolerance = {10, 75}
    );

    // Check if the HSV ranges are empty
    bool is_hsv_empty() const;

    // Select the color by clicking on the image
    void select(cv::Mat& frame_enhanced, int waitKey_delay);

    // Find centroids of the color in the HSV space
    std::optional<std::vector<Pose>> find_centroid(const cv::Mat& img_hsv);

private:
    // Callback function for mouse events (for selecting color)
    static void click_event(int event, int x, int y, int flags, void* param);

    std::string name;  // Color name
    int min_area;  // Minimum area of contour to consider
    std::tuple<int, int> hs_tolerance;  // Tolerance for HSV values
    std::string lower_hsv_file;  // File path for lower HSV range
    std::string upper_hsv_file;  // File path for upper HSV range
    cv::Mat lowerb;  // Lower HSV range
    cv::Mat upperb;  // Upper HSV range
    std::optional<std::vector<std::tuple<int, int>>> uv;  // Coordinates of centroids (if any)
};

#endif // COLOR_HPP
