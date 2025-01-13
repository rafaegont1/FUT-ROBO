#include "Video.hpp"
#include "Color.hpp"
#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>

constexpr std::string config_file = "config.yaml";

int main() {
    Video video(config_file);
    Color green("verde", 1.0);
    int key;

    try {
        green.select(video, config_file);

        do {
            video.update();
            std::optional<cv::Point> c = green.find_centroid(video.frame.hsv);
            if (c.has_value()) {
                std::cout << "x: " << c.value().x << '\n' 
                          << "y: " << c.value().y << '\n';
                cv::Point point(c.value().x, c.value().y);
                cv::circle(video.frame.raw, point, 8, cv::Scalar(255, 0, 0), 5); // rascunho
                std::string text = std::to_string(point.x) + ',' + std::to_string(point.y);
                cv::putText(video.frame.raw, text, point, cv::FONT_HERSHEY_PLAIN, 2.0, cv::Scalar(255, 0, 0));
            } else {
                std::cout << "green not found\n";
            }

            key = video.show();
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
