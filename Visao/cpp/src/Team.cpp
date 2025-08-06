#include "futbot/Team.hpp"

#include <cmath>
#include <format>
#include <print>

Team::Team(const Color& teamColor, const Color& player1Color,
    const Color& player2Color, const Calibration& calib,
    const std::string& configFile) : m_teamColor{teamColor}, m_calib{calib},
    m_players{player1Color, player2Color}
{
    readConfig(configFile);
}

void Team::readConfig(const std::string& configFile)
{
    cv::FileStorage fs(configFile, cv::FileStorage::READ);

    if (!fs.isOpened()) {
        auto errorMsg = std::format("Couldn't open file `{}`", configFile);
        throw std::runtime_error(errorMsg);
    }

    fs["color"]["rectMinArea"] >> m_rectMinArea;
    fs["color"]["circleMinArea"] >> m_circleMinArea;
    fs["color"]["roiWidth"] >> m_roiRect.width;
    fs["color"]["roiHeight"] >> m_roiRect.height;

    fs.release();
}

void Team::findPoses(Video& video)
{
    // Find centroids of figures that meet the minimum area
    std::vector<cv::Point> centroids =
        m_teamColor.findCentroids(video.frame.hsv, m_rectMinArea, 2);

    // Set players as not found
    for (auto& player : m_players) {
        player.found = false;
    }

    // std::println("centroids size: {}", centroids.size()); // rascunho

    for (const auto& centroid : centroids) {
        cv::Mat frameHsvRoi = getRoi(video, centroid);

        for (auto& player : m_players) {
            if (player.found) continue;

            std::vector<cv::Point> centroidCircle =
                player.color.findCentroids(frameHsvRoi, m_circleMinArea);
            // Continue if circle with minimum area wasn't found
            if (centroidCircle.empty()) continue;

            player.centroidRect = centroid;
            player.centroidCircle = centroidCircle.front();

#ifdef MY_DEBUG
            video.drawCircle(player.centroidRect,
                std::format("{}|{}: {},{}",
                m_teamColor.name(), player.color.name(), centroid.x, centroid.y));
#endif // MY_DEBUG

            player.found = true;
            std::println("Found player: {}|{}", m_teamColor.name(), player.color.name()); // rascunho
        }

        if (allPlayersFound()) break;
    }
}

// void Team::publish_poses(Publisher& pub, Team::MatchSide match_side)
// {
//     constexpr double RAD2DEG = 180 / M_PI;

//     // auto pub_topic = [this](const Team::Player& p, Team::MatchSide match_side) -> std::string {
//     //     const std::string home_or_away =
//     //         match_side == MatchSide::HOME ? "HOME" :
//     //         match_side == MatchSide::AWAY ? "AWAY" :
//     //         "UNKNOWN";
//     //     const char team_char = std::toupper(this->team_color.name()[0]);
//     //     const char player_char = std::toupper(p.color.name()[0]);

//     //     return home_or_away + '-' + team_char + player_char;
//     // };

//     for (const auto& p : players_) {
//         const std::string pub_msg =
//             std::to_string(p.centroid_rect_world.x) + ',' +
//             std::to_string(p.centroid_rect_world.y) + ',' +
//             std::to_string(static_cast<int>(p.theta * RAD2DEG)) + ',';
//         const std::string pub_topic = home_or_away(match_side) + '-' +
//             static_cast<char>(std::toupper(this->team_color.name()[0])) +
//             static_cast<char>(std::toupper(p.color.name()[0]));

//         // std::cout << "Publishing in topic " << pub_topic << std::endl; // rascunho
//         pub.publish(pub_msg, pub_topic);
//     }
// }

const std::array<Team::Player, 2>& Team::players() const
{
    return m_players;
}

// inline std::string Team::homeOrAway(Team::MatchSide matchSide) const
// {
//     return matchSide == MatchSide::HOME ? "HOME" :
//            matchSide == MatchSide::AWAY ? "AWAY" :
//            "UNKNOWN";
// }

cv::Mat Team::getRoi(Video& video, const cv::Point& centroid)
{
    const int topLeftX = centroid.x - m_roiRect.width / 2;
    const int topLefty = centroid.y - m_roiRect.height / 2;
    const int maxX = video.frame.hsv.cols - m_roiRect.width;
    const int maxY = video.frame.hsv.rows - m_roiRect.height;

    m_roiRect.x = std::clamp(topLeftX, 0, maxX);
    m_roiRect.y = std::clamp(topLefty, 0, maxY);

#ifdef MY_DEBUG
    video.drawRect(m_roiRect);
#endif // MY_DEBUG

    cv::Mat frameHsvRoi = video.frame.hsv(m_roiRect);

    return frameHsvRoi;
}

// double Team::getTheta(const cv::Point& rectPoint, const cv::Point& circlePoint)
// {
//     int deltaX = circlePoint.y - rectPoint.y;
//     int deltaY = circlePoint.x - rectPoint.x;
//     // std::cout << "deltaX: " << deltaX << '\n'  // rascunho
//     //           << "deltaY: " << deltaY << '\n'; // rascunho
//     return std::atan2(deltaX, deltaY);
// }

bool Team::allPlayersFound() const
{
    for (const auto& player : m_players) {
        if (!player.found) return false;
    }

    return true;
}

// void Team::invertThetaAngles()
// {
//     for (auto& player : m_players) {
//         if (player.theta > 0) {
//             player.theta -= 180.0;
//         }
//         // NOTE: aqui é `if theta<=0` ou `else`?
//         if (player.theta <= 0) {
//             player.theta += 180.0;
//         }
//     }
// }
