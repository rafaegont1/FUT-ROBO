#include <cstdlib>
#include <format>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <print>
#include <string>
// #include <chrono> // rascunho
#include "futbot/Video.hpp"
// #include "futbot/Calibration.hpp"
// #include "futbot/Color.hpp"
// #include "futbot/Team.hpp"
// #include "futbot/Publisher.hpp"
#include "futbot/Ball.hpp"

// constexpr double RAD2DEG = 180 / M_PI;
constexpr std::string configFile = "config.yaml";

// inline std::string playerCoordToString(const Team::Player& player)
// {
//     return std::format("{},{},{}", player.centroid_rect_world.x,
//         player.centroid_rect_world.y, static_cast<int>(player.theta*RAD2DEG));
// }

// int main(int argc, char* argv[])
int main()
{
    // Publisher publisher("MANAGER", "tcp://localhost:1883");

    Video video(configFile);
    // Calibration calib;

    // calib.calibrate(video);

    // Color green("verde");
    // // Color blue("azul");
    // Color pink("rosa");
    // Color yellow("amarelo");
    // // Color orange("laranja");

    // if (!green.fileLodead()) green.select(video, configFile);
    // // if (!blue.fileLodead()) blue.select(video, configFile);
    // if (!pink.fileLodead()) pink.select(video, configFile);
    // if (!yellow.fileLodead()) yellow.select(video, configFile);
    // // if (!orange.fileLodead()) orange.select(video, configFile);

    // Team teamGreen(green, pink, yellow, calib, configFile);
    // // static Team teamBlue(calib);
    Ball ball;

    ball.selectColor(video);
    ball.showSelectedColor(video);

    try {
        int key;

        do {
            // auto start_time = std::chrono::high_resolution_clock::now(); // rascunho
            video.updateFrame();

            // teamGreen.findPoses(video);
            // teamBlue.findPoses(video);
            auto ballResult = ball.findCentroid(video.frameHsv());
            if (ballResult.has_value()) {
                const auto& [ballCentroid, ballRadius] = ballResult.value();
                video.drawCircle(ballCentroid, ballRadius);
                video.putText(
                    std::format("{:.2f},{:.2f}|{:.2f}",
                        ballCentroid.x, ballCentroid.y, ballRadius
                    ),
                    ballCentroid
                );
            } else {
                std::println("Ball wasn't found!");
            }

            // team_green.publish_poses(publisher, Team::MatchSide::HOME);
            // team_blue.publish_poses(publisher, Team::MatchSide::HOME);

            // teamGreen.invertThetaAngles();
            // teamBlue.invertThetaAngles();

            // team_green.publish_poses(publisher, Team::MatchSide::AWAY);
            // team_blue.publish_poses(publisher, Team::MatchSide::AWAY);

            // ball.publish_pose(publisher);

            key = video.showFrame();
            // auto end_time = std::chrono::high_resolution_clock::now(); // rascunho
            // std::chrono::duration<double, std::milli> time = end_time - start_time; // rascunho
            // std::cout << "Took " << time.count() << " ms to run.\n"; // rascunho
        } while (key != 27);
    } catch (const std::exception& e) {
        std::println(std::cerr, "Error: {}", e.what());
        return 1;
    }

    return 0;
}
