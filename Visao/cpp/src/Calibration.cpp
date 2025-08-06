#include "futbot/Calibration.hpp"
#include <format>
#include <print>

constexpr std::string calibConfigFile = "cfg/calib.yaml"

constexpr std::array<std::array<int, 2>, 5> Calibration::XY_POINTS = {{
    {0, 0}, 
    {-1190, 800}, 
    {1190, 800}, 
    {1190, -800}, 
    {-1190, -800}
}};

cv::Mat Calibration::calculateCoeff(const std::vector<std::vector<int>>& uv_points)
{
    int n = uv_points.size();
    
    // Montando a matriz A
    cv::Mat A(n, 5, CV_64F);
    for (int i = 0; i < n; ++i) {
        double u = uv_points[i][0];
        double v = uv_points[i][1];
        A.at<double>(i, 0) = 1.0;
        A.at<double>(i, 1) = u;
        A.at<double>(i, 2) = v;
        A.at<double>(i, 3) = u * u;
        A.at<double>(i, 4) = v * v;
    }

    // Montando as matrizes B para os eixos X e Y
    cv::Mat Bx(n, 1, CV_64F);
    cv::Mat By(n, 1, CV_64F);
    for (int i = 0; i < n; ++i) {
        Bx.at<double>(i, 0) = XY_POINTS[i][0];
        By.at<double>(i, 0) = XY_POINTS[i][1];
    }

    // Calculando a pseudo-inversa de A
    cv::Mat A_inv;
    invert(A.t() * A, A_inv, cv::DECOMP_SVD);
    A_inv = A_inv * A.t();

    // Calculando os coeficientes alpha e beta
    cv::Mat alpha = A_inv * Bx;
    cv::Mat beta = A_inv * By;

    // Concatenando os coeficientes alpha e beta em uma matriz de saída
    cv::Mat coefficients;
    vconcat(alpha.t(), beta.t(), coefficients); // Concatenar como linhas

    return coefficients;
}

// Função de callback para o evento de clique
// void Calibration::clickEvent(int event, int x, int y, int, void* param)
// {
//     if (event == cv::EVENT_LBUTTONDOWN) {
//         auto uv_points = static_cast<std::vector<std::vector<int>>*>(param);
//         // std::println("Ponto selecionado: {}, {}", x, y);
//         uv_points->push_back({x, y});
//     }
// }

bool Calibration::fileRead()
{
    cv::FileStorage fs(calibConfigFile, cv::FileStorage::READ);

    if (fs.isOpened()) {
        fs["cte"] >> m_cte;
        fs.release();
        return true;
    }

    return false;
}

void Calibration::fileWrite()
{
    cv::FileStorage fs(calibConfigFile, cv::FileStorage::WRITE);
    fs << "cte" << m_cte;
    fs.release();
}

// Função de calibração
void Calibration::calibrate(Video& video)
{
    bool isFileLoaded = fileRead();

    if (isFileLoaded) {
        return;
    }

    std::vector<std::vector<int>> uvPoints;

    // Sets mouse callback function
    cv::setMouseCallback(video.windowName(),
        [](int event, int x, int y, int flags, void* userdata) -> void {
            (void)flags; // Prevent unused parameter warning
            auto& uvPointsRef =
                *static_cast<std::vector<std::vector<int>>*>(userdata);

            if (event == cv::EVENT_LBUTTONDOWN) {
                std::println("Ponto selecionado: {}, {}", x, y); // rascunho
                uvPointsRef.push_back({x, y});
            }
        },
        &uvPoints);

    // Coleta pontos UV clicando na imagem até que tenhamos o número de pontos necessário
    while (uvPoints.size() < XY_POINTS.size()) {
        video.updateFrame();
        video.putText(std::format("Select the {} point", uvPoints.size() + 1));
        int key = video.showFrame();
        if (key == 27) { // key == ESC
            exit(EXIT_SUCCESS);
        }
    }

    // Unsets mouse callback function
    cv::setMouseCallback(video.windowName(), nullptr);

    // Calcula a constante de calibração
    m_cte = calculateCoeff(uvPoints);

    fileWrite();
}

cv::Point Calibration::uvToXy(const cv::Point& uv) const
{
    // Formata os coeficientes de calibração
    cv::Mat coefs = m_cte.rowRange(0, 2);

    // Monta o vetor de entrada com o ponto UV e seus quadrados
    cv::Mat imag = (cv::Mat_<double>(1, 5) << 1.0, uv.x, uv.y, std::pow(uv.x, 2), std::pow(uv.y, 2));

    // Aplica a transformação de calibração
    cv::Mat out = coefs * imag.t();

    // Retorna as coordenadas XY arredondadas e como inteiros
    cv::Point xy;
    xy.x = static_cast<int>(std::round(out.at<double>(0, 0)));
    xy.y = static_cast<int>(std::round(out.at<double>(1, 0)));

    return xy;
}
