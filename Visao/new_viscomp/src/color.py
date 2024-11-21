import cv2 as cv
import numpy as np
from src.util import file_read, file_write


class Color:
    def __init__(self, name, min_area=100, hs_tolerance=(10, 75)):
        '''
        @param name: define o nome da cor.
        @param hs_tolerance: define os limites de tolerância, para 'hue' e
        'saturation', ao redor da cor clicada.
        '''
        self.name = name
        self.min_area = min_area
        self.hs_tolerance = hs_tolerance
        self.lower_hsv_file = f'{self.name}_lower_hsv.npy'
        self.upper_hsv_file = f'{self.name}_upper_hsv.npy'
        self.lower_hsv = file_read(self.lower_hsv_file)
        self.upper_hsv = file_read(self.upper_hsv_file)
        self.uv = None

    def is_hsv_empty(self):
        print(f'{self.lower_hsv.any() and self.upper_hsv.any()}')  # rascunho
        return not (self.lower_hsv.any() and self.upper_hsv.any())

    def select(self, frame_enhanced, waitKey_delay):
        select_window_name = f"Clique na cor desejada para '{self.name}'"
        cv.namedWindow(select_window_name)

        try:
            while not self.lower_hsv.any() and not self.upper_hsv.any():
                cv.imshow(select_window_name, frame_enhanced)
                cv.setMouseCallback(select_window_name, self.__click_event, param=frame_enhanced)
                key = cv.waitKey(waitKey_delay)
                if key == ord('q'):
                    break
        finally:
            cv.destroyWindow(select_window_name)

        frame_hsv = cv.cvtColor(frame_enhanced, cv.COLOR_BGR2HSV)
        print(f'self.lower_hsv={self.lower_hsv} | self.upper_hsv={self.upper_hsv}')  # rascunho
        mask = cv.inRange(frame_hsv, self.lower_hsv, self.upper_hsv)
        frame_hsv_masked = cv.bitwise_and(frame_hsv, frame_hsv, mask=mask)
        res = cv.cvtColor(frame_hsv_masked, cv.COLOR_HSV2BGR)

        isolation_window_name = "Isolamento da cor selecionada"
        cv.imshow(isolation_window_name, res)
        cv.waitKey(0)
        cv.destroyWindow(isolation_window_name)

        file_write(self.lower_hsv_file, self.lower_hsv)
        file_write(self.upper_hsv_file, self.upper_hsv)

    def __click_event(self, event, x, y, flags, param):
        '''
        @param param: é a imagem passada quando a função de callback é chamada
        '''
        # print('FUNÇÃO ESTÁ SENDO CHAMADA AQUI ooooooooooooooooooooooooooooooooooooooooooooooooo')  # rascunho
        if event != cv.EVENT_LBUTTONDOWN:
            return

        clicked_color = param[y, x]
        print(f'clicked_color = {clicked_color}')  # rascunho

        # Converte a cor clicada de BGR para HSV
        hsv_color = cv.cvtColor(
            np.uint8([[clicked_color]]), cv.COLOR_BGR2HSV)[0][0]
        # print(f'hsv_color = {hsv_color}')  # rascunho
        # print(f'np.clip = {np.clip(hsv_color[1] + self.hs_tolerance[1], 0, 255)}')  # rascunho

        lower_h = int(hsv_color[0]) - self.hs_tolerance[0]
        lower_s = int(hsv_color[1]) - self.hs_tolerance[1]
        # print(f'lower_h = {lower_h}')  # rascunho
        # print(f'lower_s = {lower_s}')  # rascunho
        print(f'-----------> self.lower_hsv (1) = {self.lower_hsv}')
        self.lower_hsv = np.array([
            np.clip(lower_h, 0, 179),
            np.clip(lower_s, 0, 255),
            20
        ])
        print(f'self.lower_hsv (2) = {self.lower_hsv}')

        # print(f'hsv_color[1] = {hsv_color[1]}')  # rascunho
        # print(f'self.hs_tolerance[1] = {self.hs_tolerance[1]}')  # rascunho
        # print(f'{hsv_color[1]} + {self.hs_tolerance[1]} = {hsv_color[1] + self.hs_tolerance[1]}')  # rascunho
        upper_h = int(hsv_color[0]) + self.hs_tolerance[0]
        upper_s = int(hsv_color[1]) + self.hs_tolerance[1]
        # print(f'upper_h = {upper_h}')  # rascunho
        # print(f'upper_s = {upper_s}')  # rascunho
        self.upper_hsv = np.array([
            np.clip(upper_h, 0, 179),
            np.clip(upper_s, 0, 255),
            255
        ])

        print(f"Limites definidos para a cor \'{self.name}\':")
        print(f"\tlower_hsv={self.lower_hsv}")
        print(f"\tupper_hsv={self.upper_hsv}")

    def find_centroid(self, img_hsv, multi_centroids=False):
        '''
        @param multi_centroids: se 'True', retorna uma lista com todos os
        centroides maiores que min_area; se 'False', retorna o primeiro
        centroide com área maior que min_area
        '''
        # HACK: o parâmetro 'multi_centroids' é necessário, pois exite mais de
        # um contorno, igual ou maior que a área mínima, que possui a cor do
        # time (cor do retângulo). Com isso, é necessário achar todos esses
        # centroides para verificar qual player é (rosa ou amarelo).

        mask = cv.inRange(img_hsv, self.lower_hsv, self.upper_hsv)
        contours, _ = cv.findContours(
            mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if multi_centroids:
            self.uv = []
        else:
            self.uv = None

        for contour in contours:
            area = cv.contourArea(contour)

            if area < self.min_area:
                continue
            # print(f'{self.name} area = {area}')  # rascunho

            M = cv.moments(contour)

            if M["m00"] == 0:
                continue

            uv = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
            # print(f'cor {self.name}: uv = {uv} | área = {area}')  # rascunho

            if multi_centroids:
                self.uv.append(uv)
            else:
                self.uv = uv
                break

        return self.uv
