#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
#include "Video.hpp"
#include "Calibration.hpp"
#include "Color.hpp"
#include "Team.hpp"

static const std::string config_file = "../config.yaml";

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <config.yaml file>" << std::endl;
    }

    Video video(config_file);
    int key;

    Calibration calib;
    calib.calibrate(video);

    Color green("verde");
    Color pink("rosa");
    Color yellow("amarelo");

    if (!green.file_lodead()) green.select(video, config_file);
    if (!pink.file_lodead()) pink.select(video, config_file);
    if (!yellow.file_lodead()) yellow.select(video, config_file);

    Team team_green(green, pink, yellow, calib);

    try {
        do {
            video.update();

            team_green.find_poses(video);

            key = video.show();
            // std::cout << "loop" << std::endl; // rascunho
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
