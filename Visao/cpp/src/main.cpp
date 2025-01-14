#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
#include "Video.hpp"
#include "Color.hpp"
#include "Team.hpp"

static const std::string config_file = "../config.yaml";

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <config.yaml file>" << std::endl;
    }

    Video video(config_file);
    int key;

    Color green("verde");
    Color pink("rosa");
    Color yellow("amarelo");

    green.select(video, config_file);
    pink.select(video, config_file);
    yellow.select(video, config_file);

    Team team_green(green, pink, yellow);

    try {
        do {
            video.update();

            team_green.find_centroids(video);

            key = video.show();
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
