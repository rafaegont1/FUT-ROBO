#include "Team.hpp"

Team::Team(const Color& team_color, const Color& pink, const Color& yellow)
: p1{pink}, p2{yellow}, team_color{team_color}
{
}

void Team::find_centroids(Video& video)
{
    std::vector<cv::Point> team_centroids = team_color.find_centroids(video.frame.hsv);

    p1.found = false;
    p2.found = false;

    for (const auto& centroid : team_centroids) {
        cv::Mat roi_hsv = get_roi(centroid, video);

        if (!p1.found) {
            find_player(p1, video);
        } else if (!p2.found) {
            find_player(p2, video);
        } else {
            break;
        }
    }
}

inline cv::Mat Team::get_roi(const cv::Point& center, const Video& video)
{
    cv::Range row_range(
        std::max(0, center.y - roi_sz),
        std::min(video.frame.hsv.rows, center.y + roi_sz)
    );

    cv::Range col_range(
        std::max(0, center.x - roi_sz),
        std::min(video.frame.hsv.cols, center.x + roi_sz)
    );

    return video.frame.hsv(row_range, col_range);
}

inline void Team::find_player(Team::Player& player, Video& video)
{
    std::vector<cv::Point> centroids = player.color.find_centroids(video.frame.hsv, 5.0);

    if (centroids.empty()) {
        std::cout << "Player de cor " << player.color.name() << " não encontrado" << std::endl;
        player.found = false;
    } else {
        player.centroid = centroids[0];
        player.found = true;

        std::cout << player.color.name() << " x, y = " << player.centroid.x << ", " << player.centroid.y << std::endl;
        cv::circle(video.frame.raw, player.centroid, 5, cv::Scalar(255, 0, 0), 3);
        const std::string text = std::to_string(player.centroid.x) + ',' + std::to_string(player.centroid.y);
        cv::putText(video.frame.raw, text, player.centroid, cv::FONT_HERSHEY_PLAIN, 0.8, cv::Scalar(255, 255, 0));
    }
}
