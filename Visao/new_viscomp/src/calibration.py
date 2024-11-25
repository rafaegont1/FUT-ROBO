import cv2 as cv
import numpy as np
from src.util import file_read, file_write

FILE_NAME = 'calibration.npy'
uv_points = None  # Vetor de Pontos na Imagem


def calibrate(xy_points, frame_enhanced, waitKey_delay):
    global uv_points

    uv_points = file_read(FILE_NAME)

    if not uv_points.any():
        uv_points = []
        window_name = "Clique no ponto desejado para calibracao"
        cv.namedWindow(window_name)

        while len(uv_points) < len(xy_points):
            cv.imshow(window_name, frame_enhanced)
            cv.setMouseCallback(window_name, calibrate_click_event, param=frame_enhanced)
            cv.waitKey(waitKey_delay)
            # key = cv.waitKey(waitKey_delay)
            # if key == ord('q'):
            #     break

        cv.destroyWindow(window_name)

        file_write(FILE_NAME, uv_points)

    cte = coef_calc(uv_points, xy_points)
    print("Calibração concluída!")
    print(f'cte = {cte}')  # rascunho

    return cte


def calibrate_click_event(event, x, y, flags, param):
    global uv_points

    if event != cv.EVENT_LBUTTONDOWN:
        return

    print(f"Ponto selecionado: {x}, {y}")

    uv_points.append([x, y])
    # Fecha a janela de seleção de cor


def coef_calc(uv_points, xy_points):
    # Montando a matriz A
    uvarray = np.array(uv_points)
    uvec = uvarray[:, 0][:, np.newaxis]
    vvec = uvarray[:, 1][:, np.newaxis]
    A = np.block([np.ones((len(xy_points), 1)), uvarray, (uvec**2),
                 (vvec**2)])

    # Montando as matrizes B
    Bx = np.array(xy_points)[:, 0][:, np.newaxis]
    By = np.array(xy_points)[:, 1][:, np.newaxis]

    # Calculando a pseudo-inversa
    A_ = np.linalg.inv(A.T@A)@A.T

    # Calculando os coeficientes
    alpha = (A_@Bx).T
    beta = (A_@By).T

    return alpha[0], beta[0]


def uv_to_xy(uv, cte):
    '''
    @brief: transforma coordenadas uv em xy (pixeis p/ milímetros)

    @param uv: coordenadas em pixeis
    @param cte: constantes para transformação de uv para xy
    '''
    coefs = np.vstack([cte[0], cte[1]])
    imag = np.hstack((np.ones(1), np.array(uv), np.array(uv[0]**2),
                     np.array(uv[1]**2)))[:, np.newaxis]
    out = (coefs @ imag).T

    return np.array(np.round(out[0]).astype(int), dtype=np.int_).tolist()
