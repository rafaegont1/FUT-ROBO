#include "futbot/Color.hpp"

#include <opencv2/imgproc.hpp>
#include <optional>

Color::Color()
{
}

Color::Color(const std::string& name) : m_name{name}
{
    readFile();
}

void Color::readFile()
{
    cv::FileStorage fs(std::format("cfg/{}.yaml", m_name), cv::FileStorage::READ);

    if (fs.isOpened()) {
        fs["lowerb"] >> m_lowerb;
        fs["upperb"] >> m_upperb;
        m_fileLoaded = true;
        fs.release();
    }
}

void Color::showSelectedColor(const Video& video) const
{
    cv::Mat mask;
    cv::inRange(video.frame.hsv, m_lowerb, m_upperb, mask);

    cv::Mat frameMasked;
    video.frame.raw.copyTo(frameMasked, mask);

    cv::imshow(video.windowName(), frameMasked);
    cv::waitKey();
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

void Color::select(Video& video, const std::string& configFile)
{
    cv::FileStorage fs(configFile, cv::FileStorage::READ);
    int hueTolerance = (int)fs["color"]["hue_tol"];
    int satTolerance = (int)fs["color"]["sat_tol"];
    fs.release();

    std::optional<cv::Point> clickPoint = std::nullopt;

    // Sets mouse callback function
    cv::setMouseCallback(video.windowName(),
        [](int event, int x, int y, int flags, void* userdata) -> void {
            (void)flags; // Prevent unused parameter warning
            auto& clickPointRef =
                *static_cast<std::optional<cv::Point>*>(userdata);

            if (event == cv::EVENT_LBUTTONDOWN) {
                clickPointRef = cv::Point(x, y);
            }
        },
        &clickPoint);

    // Loop until user select a color
    do {
        video.updateFrame();
        video.putText(std::format("Selecione a cor `{}`", m_name));
        int key = video.showFrame();
        if (key == 27) { // key == ESC
            exit(EXIT_SUCCESS);
        }
    } while (!clickPoint.has_value());

    // Unsets mouse callback function
    cv::setMouseCallback(video.windowName(), nullptr);

    cv::Vec3b clickHsv =
        video.frame.hsv.at<cv::Vec3b>(clickPoint->y, clickPoint->x);

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

    fs.open(std::format("cfg/{}.yaml", m_name), cv::FileStorage::WRITE);
    fs << "lowerb" << m_lowerb;
    fs << "upperb" << m_upperb;
    fs.release();

    showSelectedColor(video);
}

std::optional<cv::Point> Color::findCentroid(const cv::Mat& frameHsv) const
{
    std::optional<cv::Point> centroid = std::nullopt;

    cv::Mat mask;
    cv::inRange(frameHsv, m_lowerb, m_upperb, mask);

    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    if (!contours.empty()) {
        const auto& maxContour = *std::max_element(contours.begin(), contours.end(),
            [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
                return cv::contourArea(a) < cv::contourArea(b);
            }
        );

        cv::Moments M = cv::moments(maxContour);
        centroid.x = static_cast<int>(M.m10 / M.m00);
        centroid.y = static_cast<int>(M.m01 / M.m00);
    }

    return centroid;
}
