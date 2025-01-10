#include "Video.hpp"
#include "Color.hpp"
#include <iostream>
#include <opencv2/opencv.hpp>

constexpr std::string config_file = "config.yaml";

int main() {
    Video video(config_file);

    try {
        cv::Mat frame;
        Color green("verde", 1.0);

        video.update();
        green.select(video.frame, config_file);

        while (true) {
            video.update();
            std::optional<cv::Point> c = green.find_centroid(video.frame.raw);
            if (c.has_value()) {
                std::cout << "x: " << c.value().x << '\n' 
                          << "y: " << c.value().y << '\n';
            } else {
                std::cout << "green not found\n";
            }

// #if defined(DEBUG)
            int key = video.show();
            if (key == 27) {
                break;
            }
// #endif // defined(DEBUG)
        }
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
