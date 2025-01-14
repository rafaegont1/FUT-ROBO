#include "Video.hpp"
#include "Color.hpp"
#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>

static const std::string config_file = "../config.yaml";

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <config.yaml file>" << std::endl;
    }

    Video video(config_file);
    Color green("verde", 1, 250.0);
    int key;

#ifndef DEBUG
    std::cout << "Debug mode is enabled!" << std::endl;
#else
    std::cout << "Debug mode is disabled!" << std::endl;
#endif

    try {
        green.select(video, config_file);

        do {
            video.update();

            green.find_centroid(video);

            key = video.show();
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
