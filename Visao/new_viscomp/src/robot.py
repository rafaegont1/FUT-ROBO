import cv2 as cv
import numpy as np
from src.color import Color
from src.calibration import uv_to_xy
from typing import List, Union, Tuple


class Robot:
    def __init__(
        self, 
        name: str, 
        team_color: Color, 
        player_color: Color, 
        cte: Tuple[float, float, float], 
        xoff: int = 100, 
        roi_sz: int = 15
    ) -> None:
        """
        @param name: Nome do robô.
        @param team_color: Cor do time (objeto da classe Color).
        @param player_color: Cor do jogador (objeto da classe Color).
        @param cte: Constantes de calibração (coeficientes).
        @param xoff: Distância (em mm) entre o centro do landmark e o eixo de rotação do robô.
        @param roi_sz: Tamanho da região de interesse (ROI).
        """
        self.name: str = name
        self.team_color: Color = team_color
        self.player_color: Color = player_color
        self.cte: Tuple[float, float, float] = cte
        self.xoff: int = xoff
        self.roi_sz: int = roi_sz
        self.pose: List[Union[int, None]] = [None, None, None]

    def find_pose(self, frame: np.ndarray, frame_hsv: np.ndarray) -> List[Union[int, None]]:
        """
        Encontra a pose do robô com base nos centroides das cores do time e do jogador.

        @param frame: Imagem do quadro (frame) atual.
        @param frame_hsv: Imagem do quadro no espaço de cores HSV.
        @return: Lista contendo a posição (x, y) e a orientação (theta) do robô.
        """
        self.team_color.find_centroid(frame_hsv, multi_centroids=True)

        for team_centroid in self.team_color.uv:
            roi_offset, roi_hsv = self.__get_roi(frame_hsv, team_centroid)
            self.player_color.find_centroid(roi_hsv)

            if self.player_color.uv is not None:
                self.player_color.uv = (
                    self.player_color.uv[0] + roi_offset[0],
                    self.player_color.uv[1] + roi_offset[1]
                )
                self.team_color.uv = team_centroid
                break

        if self.player_color.uv is None:
            print('Robo não encontrado')  # rascunho
            self.pose = []
        else:
            rx, ry = uv_to_xy(self.team_color.uv, self.cte)
            theta_rad = self.__get_theta()

            self.pose = [
                int(rx - (self.xoff * np.cos(theta_rad))),  # x
                int(ry + (self.xoff * np.sin(theta_rad))),  # y
                int(np.degrees(theta_rad))                  # theta
            ]

            self.__draw_on_frame(frame)

        return self.pose

    def __get_roi(
        self,
        frame_hsv: np.ndarray,
        uv: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], np.ndarray]:
        """
        Extrai a região de interesse (ROI) ao redor de um centroide, para encontrar o jogador.

        @param frame_hsv: Imagem em HSV.
        @param uv: Coordenadas do centroide.
        @return: Tupla contendo o deslocamento do ROI e a imagem da ROI em HSV.
        """
        v_start = max(0, uv[1] - self.roi_sz)
        v_end = min(frame_hsv.shape[0], uv[1] + self.roi_sz)
        u_start = max(0, uv[0] - self.roi_sz)
        u_end = min(frame_hsv.shape[1], uv[0] + self.roi_sz)

        roi_offset = (u_start, v_start)
        roi_hsv = frame_hsv[v_start:v_end, u_start:u_end]

        return roi_offset, roi_hsv

    def __get_theta(self) -> int:
        """
        Calcula o ângulo (theta) entre o time e o jogador.

        @return: O ângulo theta em graus.
        """
        delta_v = self.player_color.uv[1] - self.team_color.uv[1]
        delta_u = self.player_color.uv[0] - self.team_color.uv[0]
        theta_rad = -np.arctan2(delta_v, delta_u)

        theta_int = int(np.round(theta_rad))

        return theta_int

    def __draw_on_frame(self, frame: np.ndarray) -> None:
        """
        Desenha o ponto do centroide e a pose do robô no quadro.

        @param frame: Imagem do quadro (frame) atual.
        """
        if self.team_color.uv is not None:
            cv.circle(frame, self.team_color.uv, 3, (0, 0, 255), -1)
            text = f"{self.name} {self.pose[0]},{self.pose[1]},{self.pose[2]}"
            cv.putText(frame, text, self.team_color.uv, cv.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 0), 1)
