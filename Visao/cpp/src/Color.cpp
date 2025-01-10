#include "Color.hpp"

Color::Color(const std::string& name, double min_area) : name{name}, min_area{min_area}
{
}

void Color::select(const Video::Frame& frame, const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);
    int hue_tol = (int)fs["color"]["hue_tol"];
    int sat_tol = (int)fs["color"]["sat_tol"];
    fs.release();

    cv::Point click_point{-1, 0};
    const std::string select_win_name = "Clique na cor desejada para '" + name + "'";
    cv::namedWindow(select_win_name);

    try {
        while (click_point.x == -1) {
            cv::imshow(select_win_name, frame.raw);
            cv::setMouseCallback(select_win_name, click_event, &click_point);
            int key = cv::waitKey(50);
            if (key == 27) {
                break;
            }
        }
    } catch (...) {
        cv::destroyWindow(select_win_name);
        throw;
    }

    cv::destroyWindow(select_win_name);

    cv::Vec3b click_hsv = frame.hsv.at<cv::Vec3b>(click_point.y, click_point.x);

    lowerb = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) - hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) - sat_tol, 0, 255),
        20
    );

    upperb = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) + hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) + sat_tol, 0, 255),
        255
    );

    cv::Mat mask;
    cv::inRange(frame.hsv, lowerb, upperb, mask);

    cv::Mat frame_hsv_masked;
    cv::bitwise_and(frame.hsv, frame.hsv, frame_hsv_masked, mask);

// #if defined(DEBUG)
    cv::Mat res;
    cv::cvtColor(frame_hsv_masked, res, cv::COLOR_HSV2BGR);

    const std::string isolation_window_name = "Isolamento da cor selecionada";
    cv::imshow(isolation_window_name, res);
    cv::waitKey(0);
    cv::destroyWindow(isolation_window_name);
// #endif // defined(DEBUG)
}

std::optional<cv::Point> Color::find_centroid(const cv::Mat& frame_hsv) {
    cv::Mat mask;
    cv::inRange(frame_hsv, lowerb, upperb, mask);

    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    centroid = std::nullopt;

    for (const auto& contour : contours) {
        double area = cv::contourArea(contour);
        if (area >= min_area) {
            std::cout << "area >= min_area\n";
            cv::Moments M = cv::moments(contour);
            centroid->x = static_cast<int>(M.m10 / M.m00);
            centroid->y = static_cast<int>(M.m01 / M.m00);
            break;
        }
    }

    return centroid;
}

void Color::click_event(int event, int x, int y, int flags, void* userdata) {
    (void)flags; // prevent unused parameter warning

    if (event == cv::EVENT_LBUTTONDOWN) {
        auto clicked_point = static_cast<cv::Point*>(userdata);
        clicked_point->x = x;
        clicked_point->y = y;
    }
}
