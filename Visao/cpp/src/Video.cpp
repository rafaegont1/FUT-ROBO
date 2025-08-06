#include "futbot/Video.hpp"

#include <format>
#include <print>
#include <stdexcept>
#include <opencv2/imgproc.hpp>

constexpr int fontName = cv::FONT_HERSHEY_PLAIN;

Video::Video(const std::string& configFile)
{
    cv::FileStorage fs(configFile, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        auto errorMsg = std::format("Couldn't open file `{}`", configFile);
        throw std::runtime_error(errorMsg);
    }

    int cameraId = (int)fs["camera"]["id"];

    m_cap.open("../testes/new/output.avi"); // rascunho
    // // m_cap.open(cameraId);
    if (!m_cap.isOpened()) {
        auto errorMsg = std::format( "Couldn't open camera of ID `{}`", cameraId);
        throw std::runtime_error(errorMsg);
    }

    m_cap.set(cv::CAP_PROP_FRAME_WIDTH, (double)fs["camera"]["width"]);
    m_cap.set(cv::CAP_PROP_FRAME_HEIGHT, (double)fs["camera"]["height"]);
    m_cap.set(cv::CAP_PROP_FPS, (double)fs["camera"]["fps"]);

    fs["window"]["name"] >> m_windowName;
    fs["window"]["delay"] >> m_windowDelay;

    cv::namedWindow(m_windowName);

    fs.release();
}

Video::~Video()
{
    m_cap.release();
    cv::destroyWindow(m_windowName);
}

void Video::updateFrame()
{
    // Get the frame from video capture
    m_cap >> frame.raw;

#ifdef MY_DEBUG
    if (frame.raw.empty()) {
        // Rewind video if `cameraId` was a path to a video file
        std::println("Rewinding video...");
        m_cap.set(cv::CAP_PROP_POS_FRAMES, 0);
        m_cap >> frame.raw;
    }
#endif

    // Create a copy of the frame in HSV color space
    cv::cvtColor(frame.raw, frame.hsv, cv::COLOR_BGR2HSV);
}

int Video::showFrame()
{
    cv::imshow(m_windowName, frame.raw);
    return cv::waitKey(m_windowDelay);
}

void Video::putText(const cv::String& text, const cv::Point& org,
    const cv::Scalar& color)
{
    cv::putText(frame.raw, text, org, fontName, 1.5, color, 2);
}

void Video::drawCircle(const cv::Point& center, const cv::String& text)
{
    cv::circle(frame.raw, center, 3, cv::Scalar(0, 0, 255), 2);
    cv::putText(frame.raw, text, center, fontName, 0.8, cv::Scalar(0, 0, 0));
}

void Video::drawRect(const cv::Rect& rect)
{
    cv::rectangle(frame.raw, rect, cv::Scalar(255, 255, 0), 2);
}
