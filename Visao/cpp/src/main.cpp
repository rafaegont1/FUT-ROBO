#include <iostream>
#include <opencv2/opencv.hpp>
#include <string>
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

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cerr << "usage: " << argv[0] << " <config.yaml file>" << std::endl;
    }

    Video video(config_file);
    Publisher pub("MANAGER", "tcp://localhost:1883");

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

    Team team_green(green, pink, yellow, calib, Team::MatchSide::HOME);
    Team team_blue(blue, pink, yellow, calib, Team::MatchSide::AWAY);
    Ball ball(orange, calib);

    try {
        int key;
        const std::array<Team::Player, 2>& green_players = team_green.players();
        const std::array<Team::Player, 2>& blue_players = team_blue.players();
        std::string msg;

        do {
            video.update();

            team_green.find_poses(video);
            msg = player_coord_to_string(green_players[0]);
            pub.publish(msg, "HOME-VR");
            msg = player_coord_to_string(green_players[1]);
            pub.publish(msg, "HOME-VA");

            team_blue.find_poses(video);
            msg = player_coord_to_string(blue_players[0]);
            pub.publish(msg, "AWAY-AR");
            msg = player_coord_to_string(blue_players[1]);
            pub.publish(msg, "AWAY-AA");

            ball.find_pose(video);
            msg = ball.centroid_msg();
            pub.publish(msg, "BALL");

            key = video.show();
        } while (key != 27);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
