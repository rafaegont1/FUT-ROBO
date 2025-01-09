import cv2 as cv
import numpy as np
from src.util import file_read, file_write
from typing import List, Optional, Tuple

FILE_NAME = 'calibration.npy'
uv_points: List[List[int]] = []  # Vetor de Pontos na Imagem (lista de coordenadas [u, v])


def calibrate(
    xy_points: List[Tuple[float, float]], 
    frame: np.ndarray, 
    waitKey_delay: int
) -> np.ndarray:
    """
    Realiza a calibração do sistema, coletando pontos UV na imagem e calculando a constante de calibração.

    @param xy_points: Lista de coordenadas (x, y) no mundo real (em milímetros).
    @param frame: Imagem com o frame melhorado, para exibição durante a calibração.
    @param waitKey_delay: Tempo de espera entre quadros (em milissegundos) para interação do usuário.
    
    @return: Constantes de calibração (cte), uma matriz numpy com os coeficientes de calibração.
    """
    global uv_points

    # Tenta ler os pontos UV de um arquivo de calibração
    uv_points = file_read(FILE_NAME)

    if not uv_points.any():
        uv_points = []
        window_name = "Clique no ponto desejado para calibração"
        cv.namedWindow(window_name)

        # Coleta pontos UV clicando na imagem até que tenhamos o número de pontos necessário
        while len(uv_points) < len(xy_points):
            cv.imshow(window_name, frame)
            cv.setMouseCallback(window_name, calibrate_click_event, param=frame)
            cv.waitKey(waitKey_delay)

        cv.destroyWindow(window_name)

        # Salva os pontos UV coletados para calibração futura
        file_write(FILE_NAME, uv_points)

    # Calcula a constante de calibração
    cte = coef_calc(uv_points, xy_points)
    print("Calibração concluída!")
    print(f'cte = {cte}')  # Rascunho de saída para visualização

    return cte


def calibrate_click_event(event: int, x: int, y: int, flags: int, param: np.ndarray) -> None:
    """
    Função de callback para o evento de clique do mouse, utilizada para coletar os pontos UV durante a calibração.

    @param event: Tipo de evento do mouse (como clique esquerdo).
    @param x: Coordenada X do clique.
    @param y: Coordenada Y do clique.
    @param flags: Flags de estado do mouse.
    @param param: Parâmetro adicional (imagem do frame) passado para o callback.
    """
    global uv_points

    if event != cv.EVENT_LBUTTONDOWN:
        return

    print(f"Ponto selecionado: {x}, {y}")

    # Adiciona o ponto UV à lista
    uv_points.append([x, y])


def coef_calc(uv_points: List[List[int]], xy_points: List[Tuple[float, float]]) -> np.ndarray:
    """
    Calcula os coeficientes de calibração a partir dos pontos UV e XY fornecidos.

    @param uv_points: Lista de pontos UV (coordenadas na imagem).
    @param xy_points: Lista de pontos XY (coordenadas no mundo real).
    
    @return: Matrizes de coeficientes alpha e beta, representando a calibração.
    """
    # Montando a matriz A
    uvarray = np.array(uv_points)
    uvec = uvarray[:, 0][:, np.newaxis]
    vvec = uvarray[:, 1][:, np.newaxis]
    A = np.block([np.ones((len(xy_points), 1)), uvarray, (uvec**2), (vvec**2)])

    # Montando as matrizes B para os eixos X e Y
    Bx = np.array(xy_points)[:, 0][:, np.newaxis]
    By = np.array(xy_points)[:, 1][:, np.newaxis]

    # Calculando a pseudo-inversa de A
    A_ = np.linalg.inv(A.T @ A) @ A.T

    # Calculando os coeficientes alpha e beta
    alpha = (A_ @ Bx).T
    beta = (A_ @ By).T

    # Retorna os coeficientes de calibração para os eixos X e Y
    return np.vstack([alpha[0], beta[0]])


def uv_to_xy(uv: List[int], cte: np.ndarray) -> List[int]:
    """
    Transforma coordenadas UV em coordenadas XY no espaço físico, utilizando as constantes de calibração.

    @param uv: Coordenadas UV em pixels (u, v) a serem convertidas.
    @param cte: Constantes de calibração calculadas para a transformação.

    @return: Coordenadas XY correspondentes aos pontos UV em unidades físicas (como milímetros).
    """
    # Formata os coeficientes de calibração
    coefs = np.vstack([cte[0], cte[1]])

    # Monta o vetor de entrada com o ponto UV e seus quadrados
    imag = np.hstack((np.ones(1), np.array(uv), np.array(uv[0]**2), np.array(uv[1]**2)))[:, np.newaxis]

    # Aplica a transformação de calibração
    out = (coefs @ imag).T

    # Retorna as coordenadas XY arredondadas e como inteiros
    return np.array(np.round(out[0]).astype(int), dtype=np.int_).tolist()
