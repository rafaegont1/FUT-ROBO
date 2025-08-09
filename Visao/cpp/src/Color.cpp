#include "futbot/Color.hpp"

#include <format>
#include <opencv2/imgproc.hpp>
#include <optional>

// constexpr std::string COLOR_CONFIG_FILE = "color.yaml";

Color::Color()
{
}

Color::Color(const std::string& name) : m_name{name}
{
}

bool Color::readFile(const std::string& filename)
{
    cv::FileStorage fs(filename, cv::FileStorage::READ);

    if (fs.isOpened()) {
        fs["lowerb"] >> m_lowerb;
        fs["upperb"] >> m_upperb;

        fs.release();

        return true;
    }

    return false;
}

bool Color::writeFile(const std::string& filename)
{
    cv::FileStorage fs(filename, cv::FileStorage::WRITE);

    if (fs.isOpened()) {
        fs << "lowerb" << m_lowerb;
        fs << "upperb" << m_upperb;

        fs.release();

        return true;
    }

    return false;
}

// static void clickEvent(int event, int x, int y, int flags, void* userdata)
// {
//     (void)flags; // Prevent unused parameter warning

//     // Set `usedata` (aka `clickPoint`) value to the clicked point coordenates
//     if (event == cv::EVENT_LBUTTONDOWN) {
//         auto clickedPoint = static_cast<std::optional<cv::Point>*>(userdata);
//         *clickedPoint = cv::Point(x, y);
//     }
// }

static cv::Vec3b getFrameColor(Video& video, const std::string& colorName)
{
    std::optional<cv::Point> clickPoint = std::nullopt;

    // Sets mouse callback function
    cv::setMouseCallback(
        video.windowName(),
        [](int event, int x, int y, int flags, void* userdata) -> void {
            (void)flags; // Prevent unused parameter warning

            if (event == cv::EVENT_LBUTTONDOWN) {
                auto& clickPointRef =
                    *static_cast<std::optional<cv::Point>*>(userdata);
                clickPointRef = cv::Point(x, y);
            }
        },
        &clickPoint
    );

    // Loop until the user select a color
    do {
        video.updateFrame();
        video.putText(std::format("Selecione a cor `{}`", colorName));
        int key = video.showFrame();
        if (key == 27) { // key == ESC
            exit(EXIT_SUCCESS);
        }
    } while (!clickPoint.has_value());

    // Unsets mouse callback function
    cv::setMouseCallback(video.windowName(), nullptr);

    // Return the selected color
    return video.frameHsv().at<cv::Vec3b>(clickPoint->y, clickPoint->x);
}

void Color::select(Video& video)
{
    constexpr int hueTolerance = 5;
    constexpr int satTolerance = 75;

    cv::Vec3b clickHsv = getFrameColor(video, m_name);

    // Store the selected hsv color
    m_lowerb = cv::Scalar(
        std::clamp(static_cast<int>(clickHsv[0]) - hueTolerance, 0, 179),
        std::clamp(static_cast<int>(clickHsv[1]) - satTolerance, 0, 255),
        20
    );
    m_upperb = cv::Scalar(
        std::clamp(static_cast<int>(clickHsv[0]) + hueTolerance, 0, 179),
        std::clamp(static_cast<int>(clickHsv[1]) + satTolerance, 0, 255),
        255
    );

    showSelection(video);
}

void Color::showSelection(const Video& video) const
{
    // Create mask with lower and upper bounds
    cv::Mat mask;
    cv::inRange(video.frameHsv(), m_lowerb, m_upperb, mask);

    // Create an masked frame using the created mask
    cv::Mat frameMasked;
    video.frame().copyTo(frameMasked, mask);

    // Show selected color
    cv::imshow(video.windowName(), frameMasked);
    cv::waitKey();
}

void Color::findContours(const cv::Mat& frameHsv,
    std::vector<std::vector<cv::Point>> &contours) const
{
    cv::Mat mask;
    cv::inRange(frameHsv, m_lowerb, m_upperb, mask);

    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
}

std::vector<std::vector<cv::Point>> Color::findNLargestContours(
    const cv::Mat& frameHsv, int n) const
{
    std::vector<std::vector<cv::Point>> contours;
    findContours(frameHsv, contours);

    std::nth_element(
        contours.begin(),
        contours.begin() + n,
        contours.end(),
        [](const auto& a, const auto& b) {
            return cv::contourArea(a) > cv::contourArea(b);
        }
    );

    contours.resize(n);

    return contours;
}

std::vector<cv::Point> Color::findLargestContour(const cv::Mat& frameHsv) const
{
    std::vector<std::vector<cv::Point>> contours;
    findContours(frameHsv, contours);

    if (contours.empty()) {
        // Return an empty contour if `contours` is empty
        return std::vector<cv::Point>();
    }

    // Find contour of maximum area
    return *std::max_element(contours.begin(), contours.end(),
        [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
            return cv::contourArea(a) < cv::contourArea(b);
        }
    );
}

//     if (!contours.empty()) {
//         const auto& maxContour = *std::max_element(contours.begin(), contours.end(),
//             [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
//                 return cv::contourArea(a) < cv::contourArea(b);
//             }
//         );

//         cv::Moments M = cv::moments(maxContour);
//         centroid->x = static_cast<int>(M.m10 / M.m00);
//         centroid->y = static_cast<int>(M.m01 / M.m00);
//     }

//     return centroid;
// }
