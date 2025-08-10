#include <cstdlib>
#include <format>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <print>
#include <string>
// #include <chrono> // rascunho
#include "futbot/Video.hpp"
#include "futbot/Calibration.hpp"
// #include "futbot/Color.hpp"
#include "futbot/Team.hpp"
// #include "futbot/Publisher.hpp"
#include "futbot/Ball.hpp"

// constexpr double RAD2DEG = 180 / M_PI;
constexpr std::string CONFIG_FILE = "config.yaml";

// inline std::string playerCoordToString(const Team::Player& player)
// {
//     return std::format("{},{},{}", player.centroid_rect_world.x,
//         player.centroid_rect_world.y, static_cast<int>(player.theta*RAD2DEG));
// }

// int main(int argc, char* argv[])
int main()
{
    // Publisher publisher("MANAGER", "tcp://localhost:1883");
    Video video(CONFIG_FILE);
    Color orange("laranja", CONFIG_FILE), green("verde", CONFIG_FILE),
        blue("azul", CONFIG_FILE), pink("rosa", CONFIG_FILE),
        yellow("amarelo", CONFIG_FILE);
    Calibration calib;
    Ball ball(orange);
    std::array<Team, 2> teams{
        Team{green, pink, yellow, CONFIG_FILE},
        Team{blue, pink, yellow, CONFIG_FILE}
    };

    try {
        int key;

        calib.calibrate(video);

        if (!orange.readFile()) orange.select(video);
        if (!green.readFile()) green.select(video);
        if (!blue.readFile()) blue.select(video);
        if (!pink.readFile()) pink.select(video);
        if (!yellow.readFile()) yellow.select(video);

        do {
            video.updateFrame();

            auto ballResult = ball.findCentroid(video.frameHsv());
            if (ballResult.has_value()) {
                const auto& [ballCentroid, ballRadius] = ballResult.value();
                video.drawCircle(ballCentroid, ballRadius, cv::Scalar(255, 0, 255));
                cv::Point2f ballRealCentroid = calib.uvToXy(ballCentroid);
                video.putText(
                    std::format("{:.2f},{:.2f}|{:.2f}",
                        ballRealCentroid.x, ballRealCentroid.y, ballRadius
                    ),
                    ballCentroid
                );
            } else {
                std::println("Ball wasn't found!");
            }

            for (auto& team : teams) {
                team.findPoses(video);
                for (const auto& player : team.players()) {
                    cv::Point2f playerRealCentroid = calib.uvToXy(player.centroidRect);
                    auto text = std::format("{:.2f},{:.2f}",
                        playerRealCentroid.x, playerRealCentroid.y);
                    video.putText(text, player.centroidRect);
                }
            }

            key = video.showFrame();
        } while (key != 27);
    } catch (const std::exception& e) {
        std::println(std::cerr, "Error: {}", e.what());
        return 1;
    }

    return 0;
}
