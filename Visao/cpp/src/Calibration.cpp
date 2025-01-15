#include "Calibration.hpp"

#include <array>

const std::array<std::array<int, 2>, 5> Calibration::XY_POINTS = {{
    {0, 0}, 
    {-1190, 800}, 
    {1190, 800}, 
    {1190, -800}, 
    {-1190, -800}
}};

cv::Mat Calibration::coef_calc(const std::vector<std::vector<int>>& uv_points)
{
    int n = uv_points.size();
    cv::Mat A(n, 5, CV_64F);
    cv::Mat Bx(n, 1, CV_64F), By(n, 1, CV_64F);

    for (int i = 0; i < n; ++i) {
        A.at<double>(i, 0) = 1.0;
        A.at<double>(i, 1) = uv_points[i][0];
        A.at<double>(i, 2) = uv_points[i][0] * uv_points[i][0];
        A.at<double>(i, 3) = uv_points[i][1];
        A.at<double>(i, 4) = uv_points[i][1] * uv_points[i][1];

        Bx.at<double>(i, 0) = std::get<0>(XY_POINTS[i]);
        By.at<double>(i, 0) = std::get<1>(XY_POINTS[i]);
    }

    // Calculando a pseudo-inversa de A
    cv::Mat A_inv = A.t() * A;
    cv::Mat A_inv_ = A_inv.inv(cv::DECOMP_SVD);  // Inversa usando SVD

    // Calculando os coeficientes alpha e beta
    cv::Mat alpha = A_inv_ * A.t() * Bx;
    cv::Mat beta = A_inv_ * A.t() * By;

    // Retorna os coeficientes de calibração
    cv::Mat result(2, 1, CV_64F);
    result.at<double>(0, 0) = alpha.at<double>(0, 0);
    result.at<double>(1, 0) = beta.at<double>(0, 0);
    
    return result;
}

// Função de callback para o evento de clique
void Calibration::calibrate_click_event(int event, int x, int y, int, void* param)
{
    if (event == cv::EVENT_LBUTTONDOWN) {
        auto uv_points = static_cast<std::vector<std::vector<int>>*>(param);
        std::cout << "Ponto selecionado: " << x << ", " << y << std::endl;
        uv_points->push_back({x, y});
    }
}

bool Calibration::file_read()
{
    cv::FileStorage fs;

    fs.open("Calibration.yaml", cv::FileStorage::READ);

    if (fs.isOpened()) {
        fs["cte"] >> cte_;
        fs.release();
        return true;
    }

    return false;
}

void Calibration::file_write()
{
    cv::FileStorage fs("Calibration.yaml", cv::FileStorage::WRITE);
    fs << "cte" << cte_;
    fs.release();
}

// Função de calibração
void Calibration::calibrate(Video& video)
{
    bool file_loaded = file_read();

    if (file_loaded) {
        return;
    }

    std::vector<std::vector<int>> uv_points;

    // Coleta pontos UV clicando na imagem até que tenhamos o número de pontos necessário
    while (uv_points.size() < XY_POINTS.size()) {
        video.update();
        cv::imshow(video.win_name(), video.frame.raw);
        cv::setMouseCallback(video.win_name(), calibrate_click_event, &uv_points);
        cv::waitKey(video.win_delay());
    }

    // Calcula a constante de calibração
    cte_ = coef_calc(uv_points);
    std::cout << "Calibração concluída!" << std::endl;
    std::cout << "cte = " << cte_ << std::endl;  // Rascunho de saída para visualização

    file_write();
}

cv::Point Calibration::uv_to_xy(const cv::Point& uv) const
{
    // Confirma que cte_ é uma matriz 2x1
    if (cte_.rows != 2 || cte_.cols != 1) {
        throw std::runtime_error("cte_ deve ser uma matriz 2x1.");
    }

    // Monta o vetor de entrada com o ponto UV
    cv::Mat imag(2, 1, CV_64F);
    imag.at<double>(0, 0) = static_cast<double>(uv.x);
    imag.at<double>(1, 0) = static_cast<double>(uv.y);

    // Aplica a transformação de calibração (2x1 * 2x1)
    cv::Mat out = cte_.mul(imag);

    // Retorna as coordenadas XY arredondadas e como inteiros
    cv::Point xy;
    xy.x = static_cast<int>(std::round(out.at<double>(0, 0)));
    xy.y = static_cast<int>(std::round(out.at<double>(1, 0)));

    return xy;
}
