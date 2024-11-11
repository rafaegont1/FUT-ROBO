import cv2 as cv
import numpy as np
from src.color import Color
from src.calibration import uv_to_xy

class Robot:
    def __init__(self, team_color, player_color, cte, xoff=100, roi_sz=15):
        '''
        @param xoff: distância (em mm) entre o centro do landmark, até o eixo de
        rotação do robô
        '''
        self.team_color = team_color
        self.player_color = player_color
        self.cte = cte
        self.xoff = xoff
        self.roi_sz = roi_sz
        self.pose = {'x': None, 'y': None, 'theta': None}

    def find_pose(self, frame, frame_hsv):
        # HACK: tenta encrontrar todos os centroides da cor do time com área
        # igual ou maior que a área mínima. Com isso, é feito um ROI para cada
        # centroide do time, para tentar encontrar a cor do player (cor do
        # círculo).

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

        # TODO: transformar o centroide do ROI para o centroide do frame
        # TODO: verificar se o 'pose' está realmente correto

        if self.player_color.uv is None:
            print('robo não encontrado')  # rascunho
            self.pose = {'x': None, 'y': None, 'theta': None}
        else:
            rx, ry = uv_to_xy(team_centroid, self.cte)
            theta_rad = self.__get_theta()

            self.pose['x'] = rx - (self.xoff * np.cos(theta_rad))
            self.pose['y'] = ry + (self.xoff * np.sin(theta_rad))
            self.pose['theta'] = np.degrees(theta_rad)

            cv.circle(frame, self.team_color.uv, 3, (0, 0, 255), -1)
            text = "(x,y,theta) = {:.2f},{:.2f},{:.2f}".format(self.pose['x'], self.pose['y'], self.pose['theta'])
            # text = f"(x,y,theta) = {self.pose['x']},{self.pose['y']},{self.pose['theta']}"
            cv.putText(frame, text, self.team_color.uv, cv.FONT_HERSHEY_PLAIN,
                       0.8, (255, 255, 0), 1)

        return self.pose

    def __get_roi(self, frame_hsv, uv):
        # Limites verticais (linhas - coordenada v)
        v_start = max(0, uv[1] - self.roi_sz)
        v_end = min(frame_hsv.shape[0], uv[1] + self.roi_sz)

        # Limites horizontais (colunas - coordenada u)
        u_start = max(0, uv[0] - self.roi_sz)
        u_end = min(frame_hsv.shape[1], uv[0] + self.roi_sz)

        # Coordenadas do início do ROI para achar o centroide em relação à
        # imagem inteira
        roi_offset = (u_start, v_start)

        # Extração da região de interesse (ROI) na imagem HSV
        return roi_offset, frame_hsv[v_start:v_end, u_start:u_end]

    def __get_theta(self):
        # Diferença entre as coordenadas verticais (v)
        delta_v = self.player_color.uv[1] - self.team_color.uv[1]

        # Diferença entre as coordenadas horizontais (u)
        delta_u = self.player_color.uv[0] - self.team_color.uv[0]

        # Calcula o ângulo em radianos usando arctan2
        theta_rad = -np.arctan2(delta_v, delta_u)  # TODO: verificar se tem o sinal de menos mesmo

        print(f'delta_v = {self.player_color.uv[1]} - {self.team_color.uv[1]} = {delta_v}')
        print(f'delta_u = {self.player_color.uv[0]} - {self.team_color.uv[0]} = {delta_u}')
        print(f'theta_rad = {theta_rad}')

        return theta_rad
