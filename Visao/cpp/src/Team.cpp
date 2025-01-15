#include "Team.hpp"
#include <opencv2/highgui.hpp>

Team::Team(const Color& team_color, const Color& pink, const Color& yellow)
: p1{pink}, p2{yellow}, team_color{team_color}
{
}

void Team::find_centroids(Video& video)
{
    std::vector<cv::Point> team_centroids = team_color.find_centroids(video.frame.hsv, 200.0, 2);
    // std::cout << "team_centroids size: " << team_centroids.size() << std::endl; // rascunho

    p1.found = false;
    p2.found = false;

    for (const auto& centroid : team_centroids) {
        cv::circle(video.frame.raw, centroid, 5, cv::Scalar(255, 0, 0), 3);
        const std::string text = std::to_string(centroid.x) + ',' + std::to_string(centroid.y);
        cv::putText(video.frame.raw, text, centroid, cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(255, 255, 0));

        ROI roi = get_roi(centroid, video);

        if (!p1.found) {
            find_player(p1, roi);
        } else if (!p2.found) {
            find_player(p2, roi);
        } else {
            break;
        }
    }

    if (!p1.found)
        std::cout << "Player de cor " << p1.color.name() << " não encontrado" << std::endl;
    if (!p2.found)
        std::cout << "Player de cor " << p2.color.name() << " não encontrado" << std::endl;
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
    std::vector<cv::Point> centroids = player.color.find_centroids(roi.frame_hsv, 5.0);

    if (centroids.empty()) {
        // std::cout << "Player de cor " << player.color.name() << " não encontrado" << std::endl;
        player.found = false;
    } else {
        player.centroid = std::move(centroids[0]);

        // Fix ROI offset
        player.centroid.x += roi.offset.x;
        player.centroid.y += roi.offset.y;

        player.found = true;

        std::cout << player.color.name() << " x, y = " << player.centroid.x << ", " << player.centroid.y << std::endl;
    }
}
