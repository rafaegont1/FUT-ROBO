#ifndef TEAM_HPP
#define TEAM_HPP

#include <array>
#include "Color.hpp"
#include "Calibration.hpp"

class Team {
public:
    struct Player {
        cv::Point centroid_circle_image;
        cv::Point centroid_circle_world;
        cv::Point centroid_rect_image;
        cv::Point centroid_rect_world;
        double theta;
        bool found = false;
        Color color;
    };

    Team(const Color& team_color, const Color& pink, const Color& yellow, const Calibration& calib);
    void find_poses(Video& video);
    const std::array<Team::Player, 2>& players();

private:
    struct ROI {
        cv::Mat frame_hsv;
        cv::Point offset;
    };

    void file_read(const std::string& config_file = "../config.yaml");
    inline Team::ROI get_roi(const cv::Point& center, const Video& video);
    // inline void find_player(Team::Player& player, cv::Point& centroid, Video& video);
    inline double get_theta(const cv::Point& rect_point, const cv::Point& circle_point);
    inline bool all_players_found();

    std::string name_;
    Color team_color;
    std::array<Player, 2> players_;
    int roi_sz_ = 15;
    const Calibration& calib_;
    double rect_min_area_;
    double circle_min_area_;
};

#endif // TEAM_HPP
