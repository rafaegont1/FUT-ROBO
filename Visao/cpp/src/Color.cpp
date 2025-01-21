#include "Color.hpp"

#include <optional>

Color::Color()
{
    file_open();
}

Color::Color(const std::string& name) : name_{name}
{
    file_open();
}

void Color::file_open()
{
    cv::FileStorage fs(name_ + ".yaml", cv::FileStorage::READ);

    if (fs.isOpened()) {
        fs["lowerb"] >> lowerb_;
        fs["upperb"] >> upperb_;
        file_loaded_ = true;
        fs.release();
    }
}

void Color::select(Video& video, const std::string& config_file)
{
    std::cout << "lowerb_: " << lowerb_.rows << ' ' << lowerb_.cols << std::endl; // rascunho
    cv::FileStorage fs;

    fs.open(config_file, cv::FileStorage::READ);
    int hue_tol = (int)fs["color"]["hue_tol"];
    int sat_tol = (int)fs["color"]["sat_tol"];
    fs.release();

    std::optional<cv::Point> click_point = std::nullopt;

    cv::setMouseCallback(video.win_name(), click_event, &click_point);
    do {
        video.update();
        // const std::string win_text = "Selecione a cor " + name_;
        // cv::putText(video.frame.raw, win_text, cv::Point(0, video.frame.raw.rows - 10), cv::FONT_HERSHEY_PLAIN, 1.5, cv::Scalar(80, 80, 80), 2);
        video.draw_text("Selecione a cor " + name_);
        int key = video.show();
        // cv::imshow(video.win_name(), video.frame.raw);
        // int key = cv::waitKey(video.win_delay());
        if (key == 27) break;
    } while (!click_point.has_value());
    cv::setMouseCallback(video.win_name(), nullptr);

    cv::Vec3b click_hsv = video.frame.hsv.at<cv::Vec3b>(click_point->y, click_point->x);
    // std::cout << "Click Point: (" << click_point->x << ", " << click_point->y << ")" // rascunho
    //       << " -> H: " << static_cast<int>(click_hsv[0]) // rascunho
    //       << ", S: " << static_cast<int>(click_hsv[1]) // rascunho
    //       << ", V: " << static_cast<int>(click_hsv[2]) << std::endl; // rascunho

    lowerb_ = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) - hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) - sat_tol, 0, 255),
        20
    );
    std::cout << "lowerb_: " << lowerb_.rows << ' ' << lowerb_.cols << std::endl; // rascunho
    // std::cout << "lowerb: (" << static_cast<int>(lowerb[0]) << ", " // rascunho
    //                          << static_cast<int>(lowerb[1]) << ", " // rascunho
    //                          << static_cast<int>(lowerb[2]) << ")" // rascunho
    //                          << std::endl; // rascunho

    upperb_ = cv::Scalar(
        std::clamp(static_cast<int>(click_hsv[0]) + hue_tol, 0, 179),
        std::clamp(static_cast<int>(click_hsv[1]) + sat_tol, 0, 255),
        255
    );
    // std::cout << "upperb: (" << static_cast<int>(upperb[0]) << ", " // rascunho
    //                          << static_cast<int>(upperb[1]) << ", " // rascunho
    //                          << static_cast<int>(upperb[2]) << ")" // rascunho
    //                          << std::endl; // rascunho

    fs.open(name_ + ".yaml", cv::FileStorage::WRITE);
    fs << "lowerb" << lowerb_;
    fs << "upperb" << upperb_;
    fs.release();

// #if defined(DEBUG)
    cv::Mat mask;
    cv::inRange(video.frame.hsv, lowerb_, upperb_, mask);

    cv::Mat frame_hsv_masked;
    cv::bitwise_and(video.frame.hsv, video.frame.hsv, frame_hsv_masked, mask);

    cv::Mat res;
    cv::cvtColor(frame_hsv_masked, res, cv::COLOR_HSV2BGR);

    cv::imshow(video.win_name(), res);
    cv::waitKey();
// #endif // defined(DEBUG)
}

const std::vector<cv::Point> Color::find_centroids(const cv::Mat& frame_hsv, double min_area, std::size_t size)
{
    std::vector<cv::Point> centroids;

    cv::Mat mask;
    cv::inRange(frame_hsv, lowerb_, upperb_, mask);

    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    for (const auto& contour : contours) {
        double area = cv::contourArea(contour);
        // std::cout << "AREA: " << area << std::endl; // rascunho

        if (area >= min_area) {
            std::cout << "color: " << name_ << '\n' // rascunho
                      << "area > min_area: " << area << std::endl; // rascunho
            // std::cout << "area >= min_area\n";
            cv::Moments M = cv::moments(contour);

            if (M.m00 != 0) {
                int x = static_cast<int>(M.m10 / M.m00);
                int y = static_cast<int>(M.m01 / M.m00);
                centroids.emplace_back(x, y);
// #ifdef DEBUG
                // std::cout << "x, y = " << x << ", " << y << std::endl;
                // cv::circle(video.frame.raw, centroids.back(), 5, cv::Scalar(255, 0, 0), 3);
                // const std::string text = std::to_string(x) + ',' + std::to_string(y);
                // cv::putText(video.frame.raw, text, centroids.back(), cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(255, 255, 0));
// #endif
                if (centroids.size() == size) {
                    break;
                }
            }
        }
    }

    return centroids;
}

void Color::click_event(int event, int x, int y, int flags, void* userdata)
{
    (void)flags; // Prevent unused parameter warning

    if (event == cv::EVENT_LBUTTONDOWN) {
        auto clicked_point = static_cast<std::optional<cv::Point>*>(userdata);
        *clicked_point = cv::Point(x, y);
    }
}

const std::string& Color::name()
{
    return name_;
}

void Color::name(const std::string& new_value)
{
    name_ = new_value;
}

bool Color::file_lodead()
{
    return file_loaded_;
}
