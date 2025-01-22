#include "futbot/Team.hpp"

#include <cmath>

Team::Team(const Color& team_color, const Color& pink, const Color& yellow, const Calibration& calib, Team::MatchSide match_side)
: team_color{team_color}, calib_{calib}, match_side_{match_side}
{
    players_[0].color = pink;
    players_[1].color = yellow;
    file_read();
}

void Team::file_read(const std::string& config_file)
{
    cv::FileStorage fs(config_file, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        throw std::runtime_error("Couldn't open file " + config_file);
    }

    fs["color"]["rect_min_area"] >> rect_min_area_;
    fs["color"]["circle_min_area"] >> circle_min_area_;

    fs.release();
}


void Team::find_poses(Video& video)
{
    std::vector<cv::Point> rect_centroids =
        team_color.find_centroids(video.frame.hsv, rect_min_area_, 2);
    // std::cout << "num of centroids: " << rect_centroids.size() << std::endl; // rascunho

    for (auto& p : players_) {
        p.found = false;
    }

    for (const auto& centroid_rect_image : rect_centroids) {
        ROI roi = get_roi(centroid_rect_image, video);

        if (all_players_found()) break;

        for (auto& p : players_) {
            if (p.found) continue;

            std::vector<cv::Point> centroid_circle_image = p.color.find_centroids(roi.frame_hsv, circle_min_area_);
            if (centroid_circle_image.empty()) continue;

            // std::cout << "Player " << p.color.name() << '\n'; // rascunho
            // std::cout << "rect" << std::endl; // rascunho
            p.centroid_rect_image = centroid_rect_image;
            p.centroid_rect_world = calib_.uv_to_xy(centroid_rect_image);

            // std::cout << "circle" << std::endl; // rascunho
            p.centroid_circle_image = centroid_circle_image[0];
            // Fix ROI offset
            p.centroid_circle_image.x += roi.offset.x;
            p.centroid_circle_image.y += roi.offset.y;
            p.centroid_circle_world = calib_.uv_to_xy(p.centroid_circle_image);

            p.theta = get_theta(p.centroid_rect_world, p.centroid_circle_world);
            // std::cout << "theta: " << p.theta << " rad\n" // rascunho
            //           << "theta: " << p.theta*180/M_PI << " °\n"; // rascunho

            video.draw_circle(
                p.centroid_rect_image,
                team_color.name() + '|' + p.color.name() + '=' + std::to_string(p.centroid_rect_world.x) + ',' + std::to_string(p.centroid_rect_world.y) + ',' + std::to_string(p.theta*180/M_PI)
            );

            p.found = true;
        }
    }
}

void Team::publish_poses(Publisher& pub)
{
    auto msg_to_publish = [](const Team::Player& p) -> std::string {
        constexpr double RAD2DEG = 180 / M_PI;

        return std::to_string(p.centroid_rect_world.x) + ',' +
               std::to_string(p.centroid_rect_world.y) + ',' +
               std::to_string(static_cast<int>(p.theta * RAD2DEG)) + ',';
    };

    for (const auto& p : players_) {
        pub.publish(msg_to_publish(p), home_or_away());
    }
}

const std::array<Team::Player, 2>& Team::players() const
{
    return players_;
}

std::string Team::home_or_away() const
{
    return match_side_ == MatchSide::HOME ? "HOME" :
           match_side_ == MatchSide::AWAY ? "AWAY" :
           "UNKNOWN";
}

Team::ROI Team::get_roi(const cv::Point& center, const Video& video)
{
    ROI roi;

    int v_start = std::max(0, center.y - roi_sz_);
    int v_end = std::min(video.frame.hsv.rows, center.y + roi_sz_);
    int u_start = std::max(0, center.x - roi_sz_);
    int u_end = std::min(video.frame.hsv.cols, center.x + roi_sz_);

    cv::Range row_range(v_start, v_end);
    cv::Range col_range(u_start, u_end);

    roi.frame_hsv = video.frame.hsv(row_range, col_range);
    roi.offset.x = u_start;
    roi.offset.y = v_start;

    return roi;
}

double Team::get_theta(const cv::Point& rect_point, const cv::Point& circle_point)
{
    int delta_x = circle_point.y - rect_point.y;
    int delta_y = circle_point.x - rect_point.x;
    // std::cout << "delta_x: " << delta_x << '\n'  // rascunho
    //           << "delta_y: " << delta_y << '\n'; // rascunho

    return std::atan2(delta_x, delta_y);
}

bool Team::all_players_found()
{
    for (const auto& p : players_) {
        if (!p.found) return false;
    }

    return true;
}
