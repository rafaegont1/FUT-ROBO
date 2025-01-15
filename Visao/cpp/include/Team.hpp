#ifndef TEAM_HPP
#define TEAM_HPP

#include "Color.hpp"
#include "Calibration.hpp"

class Team {
public:
    struct Player {
        Player(const Color& color) : color{color} {}
        cv::Point centroid;
        double theta;
        bool found = false;
        Color color;
    };

    Team(const Color& team_color, const Color& pink, const Color& yellow, const Calibration& calib);
    void find_poses(Video& video);

    Player p1;
    Player p2;

private:
    struct ROI {
        cv::Mat frame_hsv;
        cv::Point offset;
    };

    inline Team::ROI get_roi(const cv::Point& center, const Video& video);
    inline void find_player(Team::Player& player, const Team::ROI& roi);
    inline int get_theta(const cv::Point& rect_point, const cv::Point& circle_point);

    std::string name_;
    Color team_color;
    int roi_sz = 15;
    const Calibration& calib;
};

#endif // TEAM_HPP
