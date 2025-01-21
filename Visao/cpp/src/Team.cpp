#include "Team.hpp"

#include <opencv2/highgui.hpp>
#include <cmath>

Team::Team(const Color& team_color, const Color& pink, const Color& yellow, const Calibration& calib)
: team_color{team_color}, calib_{calib}
{
    players_[0].color = pink;
    players_[1].color = yellow;
}

void Team::find_poses(Video& video)
{
    std::vector<cv::Point> rect_centroids =
        team_color.find_centroids(video.frame.hsv, 200.0, 2);
    std::cout << "num of centroids: " << rect_centroids.size() << std::endl; // rascunho

    // p1.found = false;
    // p2.found = false;
    for (auto& p : players_) {
        p.found = false;
    }

    for (const auto& centroid_rect_image : rect_centroids) {
        ROI roi = get_roi(centroid_rect_image, video);

        if (all_players_found()) break;

        for (auto& p : players_) {
            if (p.found) continue;
            std::vector<cv::Point> centroid_circle_image = p.color.find_centroids(roi.frame_hsv, 10.0);
            if (centroid_circle_image.empty()) continue;
            p.centroid_rect_image = centroid_rect_image;
            std::cout << "Player " << p.color.name() << '\n'; // rascunho
            std::cout << "rect" << std::endl; // rascunho
            p.centroid_rect_world = calib_.uv_to_xy(centroid_rect_image);
            p.centroid_circle_image = centroid_circle_image[0];
            // Fix ROI offset
            p.centroid_circle_image.x += roi.offset.x;
            p.centroid_circle_image.y += roi.offset.y;
            std::cout << "circle" << std::endl; // rascunho
            cv::Point centroid_circle_world = calib_.uv_to_xy(p.centroid_circle_image);
            p.theta = get_theta(p.centroid_rect_world, centroid_circle_world);
            std::cout << "theta: " << p.theta << " rad\n" // rascunho
                      << "theta: " << p.theta*180/M_PI << " °\n"; // rascunho
            video.draw_circle(
                p.centroid_rect_image,
                team_color.name() + '|' + p.color.name() + '=' + std::to_string(p.centroid_rect_world.x) + ',' + std::to_string(p.centroid_rect_world.y) + ',' + std::to_string(p.theta*180/M_PI)
            );
            p.found = true;
        }
    }
}

inline Team::ROI Team::get_roi(const cv::Point& center, const Video& video)
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

    // const std::string win_name = "ROI"; // rascunho
    // cv::namedWindow(win_name); // rascunho
    // cv::imshow(win_name, roi.frame_hsv); // rascunho
    // cv::waitKey(); // rascunho
    // cv::destroyWindow(win_name); // rascunho

    return roi;
}

// inline void Team::find_player(Team::Player& player, cv::Point& centroid, Video& video)
// {
//     std::vector<cv::Point> circle_centroid =
//         player.color.find_centroids(roi.frame_hsv, 10.0);

//     if (!circle_centroid.empty()) {
//         player.centroid_circle_image = std::move(circle_centroid[0]);

//         // Fix ROI offset
//         player.centroid_circle_image.x += roi.offset.x;
//         player.centroid_circle_image.y += roi.offset.y;

//         std::cout << "Player " << player.color.name() << '\n'; // rascunho

//         player.found = true;
//     }
// }

inline double Team::get_theta(const cv::Point& rect_point, const cv::Point& circle_point)
{
    int delta_x = circle_point.y - rect_point.y;
    int delta_y = circle_point.x - rect_point.x;
    std::cout << "delta_x: " << delta_x << '\n'  // rascunho
              << "delta_y: " << delta_y << '\n'; // rascunho

    return std::atan2(delta_x, delta_y);
}

inline bool Team::all_players_found()
{
    for (const auto& p : players_) {
        if (!p.found) return false;
    }

    return true;
}
