#ifndef TEAM_HPP
#define TEAM_HPP

#include "futbot/Color.hpp"
#include "futbot/Calibration.hpp"
#include "futbot/Publisher.hpp"

class Team {
public:
    enum class MatchSide {
        HOME,
        AWAY,
    };

    struct Player {
        std::string name;
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
    void publish_poses(Publisher& pub, Team::MatchSide match_side);
    inline std::string home_or_away(Team::MatchSide match_side) const;
    const std::array<Team::Player, 2>& players() const;
    void invert_theta_angles();

private:
    struct ROI {
        cv::Mat frame_hsv;
        cv::Point offset;
    };

    void file_read(const std::string& config_file = "../config.yaml");
    Team::ROI get_roi(const cv::Point& center, const Video& video);
    // void find_player(Team::Player& player, cv::Point& centroid, Video& video);
    double get_theta(const cv::Point& rect_point, const cv::Point& circle_point);
    bool all_players_found();

    std::string name_;
    Color team_color;
    std::array<Player, 2> players_;
    int roi_sz_;
    const Calibration& calib_;
    double rect_min_area_;
    double circle_min_area_;
    // Team::MatchSide match_side_;
};

#endif // TEAM_HPP
