import cv2 as cv
import numpy as np
from src.robot import Robot
from src.ball import Ball
from src.calibration import calibrate
from src.color import Color
from typing import List, Tuple, Optional


# Calibration constructor arguments
XY_POINTS = [(0, 0), (-1190, 800), (1190, 800), (1190, -800), (-1190, -800)]


class VisComp:
    def __init__(self, frame_enhanced: np.ndarray, waitKey_delay: int) -> None:
        """
        Constrói um objeto VisComp, responsável por inicializar os robôs e a bola com base nas cores 
        selecionadas e na calibração da câmera.

        @param frame_enhanced: Imagem do frame a ser utilizada para calibração e seleção de cores.
        @param waitKey_delay: Delay de espera entre os quadros para interação do usuário.
        """
        cte = calibrate(XY_POINTS, frame_enhanced, waitKey_delay)

        # Inicialização das cores para cada objeto (laranja, verde, azul, rosa, amarelo)
        orange = Color('laranja', min_area=150, hs_tolerance=(5, 75))
        if orange.is_hsv_empty():
            orange.select(frame_enhanced, waitKey_delay)

        green = Color('verde', min_area=10)
        if green.is_hsv_empty():
            green.select(frame_enhanced, waitKey_delay)

        blue = Color('azul', min_area=10)
        if blue.is_hsv_empty():
            blue.select(frame_enhanced, waitKey_delay)

        pink = Color('rosa', min_area=1, hs_tolerance=(10, 65))
        if pink.is_hsv_empty():
            pink.select(frame_enhanced, waitKey_delay)

        yellow = Color('amarelo', min_area=1, hs_tolerance=(5, 65))
        if yellow.is_hsv_empty():
            yellow.select(frame_enhanced, waitKey_delay)

        # Inicialização dos robôs e da bola
        self.robot_aa: Robot = Robot('AA', blue, yellow, cte)
        self.robot_ar: Robot = Robot('AR', blue, pink, cte)
        self.robot_va: Robot = Robot('VA', green, yellow, cte)
        self.robot_vr: Robot = Robot('VR', green, pink, cte)
        self.ball: Ball = Ball(orange, cte)

    def find_poses(self, frame: np.ndarray, frame_hsv: np.ndarray) -> List[Optional[Tuple[int, int]]]:
        """
        Encontra as poses de todos os robôs e da bola na imagem, retornando suas coordenadas.

        @param frame: Imagem do frame a ser processado.
        @param frame_hsv: Imagem do frame no espaço de cor HSV, usada para segmentação.

        @return: Lista de coordenadas (tuplas) representando as poses de cada robô e da bola.
        """
        poses: List[Optional[Tuple[int, int]]] = []

        # Encontra as poses para cada robô e a bola
        poses.append(self.robot_aa.find_pose(frame, frame_hsv))
        poses.append(self.robot_ar.find_pose(frame, frame_hsv))
        poses.append(self.robot_va.find_pose(frame, frame_hsv))
        poses.append(self.robot_vr.find_pose(frame, frame_hsv))
        poses.append(self.ball.find_pose(frame, frame_hsv))

        return poses
