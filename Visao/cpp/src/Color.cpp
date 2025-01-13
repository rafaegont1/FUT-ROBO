#include "Color.hpp"

Color::Color(const std::string& name, double min_area) : name{name}, min_area{min_area}
{
}

void Color::select(Video& video, const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);
    int hue_tol = (int)fs["color"]["hue_tol"];
    int sat_tol = (int)fs["color"]["sat_tol"];
    fs.release();

    std::optional<cv::Point> click_point = std::nullopt;

    do {
        video.update();
        cv::imshow(video.win_name(), video.frame.raw);
        cv::setMouseCallback(video.win_name(), click_event, &click_point);
        int key = cv::waitKey(video.win_delay());
        if (key == 27) break;
    } while (!click_point.has_value());

    cv::Vec3b click_hsv = video.frame.hsv.at<cv::Vec3b>(click_point->y, click_point->x);
    // std::cout << "Click Point: (" << click_point->x << ", " << click_point->y << ")" // rascunho
    //       << " -> H: " << static_cast<int>(click_hsv[0]) // rascunho
    //       << ", S: " << static_cast<int>(click_hsv[1]) // rascunho
    //       << ", V: " << static_cast<int>(click_hsv[2]) << std::endl; // rascunho

    lowerb = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) - hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) - sat_tol, 0, 255),
        20
    );
    // std::cout << "lowerb: (" << static_cast<int>(lowerb[0]) << ", " // rascunho
    //                          << static_cast<int>(lowerb[1]) << ", " // rascunho
    //                          << static_cast<int>(lowerb[2]) << ")" // rascunho
    //                          << std::endl; // rascunho

    upperb = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) + hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) + sat_tol, 0, 255),
        255
    );
    // std::cout << "upperb: (" << static_cast<int>(upperb[0]) << ", " // rascunho
    //                          << static_cast<int>(upperb[1]) << ", " // rascunho
    //                          << static_cast<int>(upperb[2]) << ")" // rascunho
    //                          << std::endl; // rascunho

// #if defined(DEBUG)
    cv::Mat mask;
    cv::inRange(video.frame.hsv, lowerb, upperb, mask);

    cv::Mat frame_hsv_masked;
    cv::bitwise_and(video.frame.hsv, video.frame.hsv, frame_hsv_masked, mask);

    cv::Mat res;
    cv::cvtColor(frame_hsv_masked, res, cv::COLOR_HSV2BGR);

    cv::imshow(video.win_name(), res);
    cv::waitKey(0);
// #endif // defined(DEBUG)
}

std::optional<cv::Point> Color::find_centroid(const cv::Mat& frame_hsv) {
    cv::Mat mask;
    cv::inRange(frame_hsv, lowerb, upperb, mask);

    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    for (const auto& contour : contours) {
        double area = cv::contourArea(contour);
        // std::cout << "AREA: " << area << std::endl; // rascunho

        if (area >= min_area) {
            // std::cout << "area >= min_area\n";
            cv::Moments M = cv::moments(contour);

            if (M.m00 != 0) {
                int x = static_cast<int>(M.m10 / M.m00);
                int y = static_cast<int>(M.m01 / M.m00);
                return cv::Point(x, y);
            }
        }
    }

    return std::nullopt;
}

void Color::click_event(int event, int x, int y, int flags, void* userdata) {
    (void)flags; // prevent unused parameter warning

    if (event == cv::EVENT_LBUTTONDOWN) {
        auto clicked_point = static_cast<std::optional<cv::Point>*>(userdata);
        *clicked_point = cv::Point(x, y);
    }
}
