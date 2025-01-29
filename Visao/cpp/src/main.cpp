#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
#include <chrono> // rascunho
#include "futbot/Video.hpp"
#include "futbot/Calibration.hpp"
#include "futbot/Color.hpp"
#include "futbot/Team.hpp"
#include "futbot/Publisher.hpp"
#include "futbot/Ball.hpp"

static const std::string config_file = "../config.yaml";
constexpr double RAD2DEG = 180 / M_PI;

inline std::string player_coord_to_string(const Team::Player& p)
{
    return std::to_string(p.centroid_rect_world.x) + ',' +
           std::to_string(p.centroid_rect_world.y) + ',' +
           std::to_string(static_cast<int>(p.theta*RAD2DEG)) + ',';
}

// int main(int argc, char* argv[])
int main()
{
    // if (argc < 2) {
    //     std::cerr << "usage: " << argv[0] << " <config.yaml file>" << std::endl;
    // }

    Video video(config_file);
    Publisher publisher("MANAGER", "tcp://localhost:1883");

    Calibration calib;
    calib.calibrate(video);

    Color green("verde");
    Color blue("azul");
    Color pink("rosa");
    Color yellow("amarelo");
    Color orange("laranja");

    if (!green.file_lodead()) green.select(video, config_file);
    if (!blue.file_lodead()) blue.select(video, config_file);
    if (!pink.file_lodead()) pink.select(video, config_file);
    if (!yellow.file_lodead()) yellow.select(video, config_file);
    if (!orange.file_lodead()) orange.select(video, config_file);

    Team team_green(green, pink, yellow, calib);
    Team team_blue(blue, pink, yellow, calib);
    Ball ball(orange, calib);

    try {
        int key;

        do {
            // auto start_time = std::chrono::high_resolution_clock::now(); // rascunho
            video.update();

            team_green.find_poses(video);
            team_blue.find_poses(video);
            ball.find_pose(video);

            team_green.publish_poses(publisher, Team::MatchSide::HOME);
            team_blue.publish_poses(publisher, Team::MatchSide::HOME);

            team_green.invert_theta_angles();
            team_blue.invert_theta_angles();

            team_green.publish_poses(publisher, Team::MatchSide::AWAY);
            team_blue.publish_poses(publisher, Team::MatchSide::AWAY);

            ball.publish_pose(publisher);

            key = video.show();
            // auto end_time = std::chrono::high_resolution_clock::now(); // rascunho
            // std::chrono::duration<double, std::milli> time = end_time - start_time; // rascunho
            // std::cout << "Took " << time.count() << " ms to run.\n"; // rascunho
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
