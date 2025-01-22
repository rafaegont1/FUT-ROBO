#include "futbot/Calibration.hpp"

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
void Calibration::click_event(int event, int x, int y, int, void* param)
{
    if (event == cv::EVENT_LBUTTONDOWN) {
        auto uv_points = static_cast<std::vector<std::vector<int>>*>(param);
        // std::cout << "Ponto selecionado: " << x << ", " << y << std::endl;
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

    // Sets mouse callback function
    cv::setMouseCallback(video.win_name(), click_event, &uv_points);

    // Coleta pontos UV clicando na imagem até que tenhamos o número de pontos necessário
    while (uv_points.size() < XY_POINTS.size()) {
        video.update();
        video.draw_text("Select the " + std::to_string(uv_points.size() + 1) + " point");
        int key = video.show();
        if (key == 27) exit(EXIT_SUCCESS);
        // cv::imshow(video.win_name(), video.frame.raw);
        // cv::waitKey(video.win_delay());
    }

    // Unsets mouse callback function
    cv::setMouseCallback(video.win_name(), nullptr);

    // Calcula a constante de calibração
    cte_ = coef_calc(uv_points);
    // std::cout << "Calibração concluída!" << std::endl;
    // std::cout << "cte = " << cte_ << std::endl;  // Rascunho de saída para visualização

    file_write();
}

cv::Point Calibration::uv_to_xy(const cv::Point& uv) const
{
// std::vector<int> uv_to_xy(const std::vector<int>& uv, const cv::Mat& cte) {
    /**
     * Transforma coordenadas UV em coordenadas XY no espaço físico, utilizando as constantes de calibração.
     *
     * @param uv: Coordenadas UV em pixels (u, v) a serem convertidas.
     * @param cte: Constantes de calibração calculadas para a transformação.
     *
     * @return: Coordenadas XY correspondentes aos pontos UV em unidades físicas (como milímetros).
     */

    // Formata os coeficientes de calibração
    cv::Mat coefs = cte_.rowRange(0, 2);

    // Monta o vetor de entrada com o ponto UV e seus quadrados
    cv::Mat imag = (cv::Mat_<double>(1, 5) << 1.0, uv.x, uv.y, std::pow(uv.x, 2), std::pow(uv.y, 2));

    // Aplica a transformação de calibração
    cv::Mat out = coefs * imag.t();

    // Retorna as coordenadas XY arredondadas e como inteiros
    // std::vector<int> xy = {static_cast<int>(std::round(out.at<double>(0, 0))),
    //                        static_cast<int>(std::round(out.at<double>(1, 0)))};
    cv::Point xy;
    xy.x = static_cast<int>(std::round(out.at<double>(0, 0)));
    xy.y = static_cast<int>(std::round(out.at<double>(1, 0)));

    // std::cout << "(u, v): " << uv.x << '\t' << uv.y << '\n'  // rascunho
    //           << "(x, y): " << xy.x << '\t' << xy.y << '\n'; // rascunho

    return xy;
}
