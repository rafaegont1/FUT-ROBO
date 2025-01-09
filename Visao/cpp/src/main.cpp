#include "Video.hpp"
#include <iostream>
#include <opencv2/opencv.hpp>

int main() {
    Video video("config.yaml");

    try {
        cv::Mat frame;

        while (true) {
            video.update();

// #if defined(DEBUG)
            int key = video.show();
            if (key == 27) { // 'ESC' key
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
