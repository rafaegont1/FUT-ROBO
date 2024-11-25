import cv2 as cv
from src.color import Color
from src.calibration import uv_to_xy
import numpy as np


class Ball:
    def __init__(self, color: Color, cte: np.ndarray) -> None:
        """
        Inicializa um objeto Ball com a cor e constante de calibração fornecida.

        @param color: Objeto Color que representa a cor da bola.
        @param cte: Constante de calibração para conversão de coordenadas UV para XY.
        """
        self.color: Color = color
        self.pose: list[float] = [None, None]  # Posição da bola, [x, y]
        self.cte: np.ndarray = cte  # Constante de calibração (por exemplo, uma matriz de transformação)

    def find_pose(self, frame: np.ndarray, frame_hsv: np.ndarray) -> list[int] | None:
        """
        Encontra a posição da bola no frame fornecido, usando a cor para encontrar o centróide.

        @param frame: Imagem do frame (BGR).
        @param frame_hsv: Imagem do frame em espaço de cores HSV.
        @return: Lista com a posição da bola [x, y] se encontrada, ou None caso contrário.
        """
        self.color.find_centroid(frame_hsv)

        if self.color.uv is None:
            print('Ball not found')
            return None

        self.pose[0], self.pose[1] = uv_to_xy(self.color.uv, self.cte)

        # Desenha um círculo no centróide da bola e exibe a posição no frame
        cv.circle(frame, self.color.uv, 3, (255, 0, 0), -1)  # Desenha um ponto azul no centro da bola
        text = f"ball {self.pose[0]},{self.pose[1]}"
        cv.putText(frame, text, self.color.uv, cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)  # Coloca o texto

        return self.pose  # Retorna a posição [x, y] da bola
