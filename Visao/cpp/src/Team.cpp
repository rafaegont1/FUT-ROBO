#include "Team.hpp"

#include <opencv2/highgui.hpp>
#include <cmath>

Team::Team(const Color& team_color, const Color& pink, const Color& yellow, const Calibration& calib)
: p1{pink}, p2{yellow}, team_color{team_color}, calib{calib}
{
}

void Team::find_poses(Video& video)
{
    std::vector<cv::Point> rect_centroids =
        team_color.find_centroids(video.frame.hsv, 200.0, 2);
    // std::cout << "team_centroids size: " << team_centroids.size() << std::endl; // rascunho

    p1.found = false;
    p2.found = false;

    for (const auto& centroid : rect_centroids) {
        ROI roi = get_roi(centroid, video);

        if (!p1.found) {
            find_player(p1, roi);
        }

        if (!p2.found) {
            find_player(p2, roi);
        }
    }

    // if (p1.found) {
    //     cv::circle(video.frame.raw, p1.centroid, 5, cv::Scalar(0, 0, 255), 3);
    //     const std::string text = std::to_string(p1.centroid.x) + ',' + std::to_string(p1.centroid.y);
    //     cv::putText(video.frame.raw, text, p1.centroid, cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(255, 255, 0));
    // }
    // if (p2.found) {
    //     cv::circle(video.frame.raw, p2.centroid, 5, cv::Scalar(0, 0, 255), 3);
    //     const std::string text = std::to_string(p2.centroid.x) + ',' + std::to_string(p2.centroid.y);
    //     cv::putText(video.frame.raw, text, p2.centroid, cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(255, 255, 0));
    // }
}

inline Team::ROI Team::get_roi(const cv::Point& center, const Video& video)
{
    ROI roi;

    int v_start = std::max(0, center.y - roi_sz);
    int v_end = std::min(video.frame.hsv.rows, center.y + roi_sz);
    int u_start = std::max(0, center.x - roi_sz);
    int u_end = std::min(video.frame.hsv.cols, center.x + roi_sz);

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

inline void Team::find_player(Team::Player& player, const Team::ROI& roi)
{
    std::vector<cv::Point> circle_centroid =
        player.color.find_centroids(roi.frame_hsv, 2.5);

    if (!circle_centroid.empty()) {
        player.centroid = std::move(circle_centroid[0]);

        // Fix ROI offset
        player.centroid.x += roi.offset.x;
        player.centroid.y += roi.offset.y;

        // Transform from uv (pixels) coordinates to xy (mm)
        player.centroid = calib.uv_to_xy(player.centroid);

        player.found = true;

        std::cout << player.color.name() << "\tx, y = " << player.centroid.x << ", " << player.centroid.y << std::endl;
    }
}

inline int Team::get_theta(const cv::Point& rect_point, const cv::Point& circle_point)
{
    int delta_v = circle_point.y - rect_point.y;
    int delta_u = circle_point.x - rect_point.x;

    return -std::atan2(delta_v, delta_u);
}
