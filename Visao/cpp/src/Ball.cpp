#include "futbot/Ball.hpp"

#include <opencv2/imgproc.hpp>

Ball::Ball()
{
}

Ball::~Ball()
{
}

static cv::Vec3b getFrameColor(Video& video)
{
    std::optional<cv::Point> clickPoint = std::nullopt;

    // Sets mouse callback function
    cv::setMouseCallback(video.windowName(),
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
        video.putText("Selecione a cor bola");
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

void Ball::selectColor(Video& video)
{
    constexpr int hueTolerance = 5;
    constexpr int satTolerance = 75;

    cv::Vec3b clickHsv = getFrameColor(video);

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
}

void Ball::showSelectedColor(const Video& video) const
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

std::optional<std::tuple<cv::Point2f, float>> Ball::findCentroid(
    const cv::Mat& frame) const
{
    // Create mask with lower and upper bounds
    cv::Mat mask;
    cv::inRange(frame, m_lowerb, m_upperb, mask);

    // Find contours using created mask
    std::vector<std::vector<cv::Point>> contours;
    cv::findContours(mask, contours, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);

    // None countours were found
    if (contours.empty()) {
        return std::nullopt;
    }

    // Find contour of maximum area
    const auto& maxContour = *std::max_element(contours.begin(), contours.end(),
        [](const std::vector<cv::Point>& a, const std::vector<cv::Point>& b) {
            return cv::contourArea(a) < cv::contourArea(b);
        }
    );

    // Find circle centroid
    cv::Point2f centroid;
    float radius;
    cv::minEnclosingCircle(maxContour, centroid, radius);

    // Return tuple with circle centroid and radius. To get values, use:
    // auto [centroid, radius] = ball.findCentroid(frame);
    return std::make_tuple(centroid, radius);
}
