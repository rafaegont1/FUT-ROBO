#!/usr/bin/env python3

import cv2 as cv
import numpy as np

# Video capture
cap = None
CAMERA_ID = 'testes/new/output.avi'
CAP_WIDTH = 800
CAP_HEIGHT = 600
CAP_FPS = 30
# Video frame
frame = None
waitKey_delay = 40  # ms
# Pontos reais conhecidos no campo:
XY_POINTS = [(0, 0), (-1190, 800), (1190, 800), (1190, -800), (-1190, -800)]


def init_capture():
    global cap

    cap = cv.VideoCapture(CAMERA_ID)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)
    cap.set(cv.CAP_PROP_AUDIO_SAMPLES_PER_SECOND, CAP_FPS)

    if not cap.isOpened():
        raise RuntimeError("Não foi possível abrir a câmera.")


def enhance_contrast(frame, ksize=5):
    '''
    @brief: Aumenta o contraste e aplica desfoque à imagem.

    @param frame: imagem a ser melhorada
    @param ksize: tamanho do kernel para a suavização
    @return: a imagem com contraste aumentado e suavizada.
    '''
    # Converte para o espaço de cores LAB
    lab = cv.cvtColor(frame, cv.COLOR_BGR2LAB)

    # Divide os canais L, A, B
    l, a, b = cv.split(lab)

    # Aplica CLAHE no canal L
    clahe = cv.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    # Une os canais L ajustado, A e B
    limg = cv.merge((cl, a, b))

    # Converte de volta para BGR
    frame_enhanced = cv.cvtColor(limg, cv.COLOR_LAB2BGR)

    # Aplica suavização usando desfoque Gaussiano
    blurred_frame = cv.GaussianBlur(frame_enhanced, (ksize, ksize), 0)

    return blurred_frame


def uv_to_xy(uv, cte):
    '''
    @brief: transforma coordenadas uv em xy (pixeis p/ milímetros)

    @param uv: coordenadas em pixeis
    @param cte: constantes para transformação de uv para xy
    '''
    coefs = np.vstack([cte[0], cte[1]])
    imag = np.hstack((np.ones(1), np.array(uv), np.array(uv[0]**2),
                     np.array(uv[1]**2)))[:, np.newaxis]
    out = (coefs@imag).T

    return np.array(out[0].round(0), dtype=np.int_).tolist()


class Calibration:
    def __init__(self, xy_points):
        '''
        @param xy_points: pontos reais conhecidos no campo
        '''
        self.xy_points = xy_points
        self.uv_points = []  # Vetor de Pontos na Imagem
        self.cte = None  # Constantes para transformação de coordenada

    def select_points(self):
        global cap, frame, waitKey_delay

        window_name = "Clique no ponto desejado para calibracao"
        cv.namedWindow(window_name)

        while len(self.uv_points) < len(self.xy_points):
            ret, frame = cap.read()

            if not ret:
                # raise RuntimeError("Falha ao capturar o frame da câmera.")
                # HACK: reiniciar o vídeo quando ele chega ao fim
                cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # rascunho
                print('Rewinding video...')  # rascunho
                continue  # rascunho

            frame_enhanced = enhance_contrast(frame)
            cv.imshow(window_name, frame_enhanced)
            cv.setMouseCallback(window_name, self.__click_event,
                                param=frame_enhanced)
            key = cv.waitKey(waitKey_delay)

            if key == ord('q'):
                break

        self.cte = self.__coef_calc()
        print("Calibração concluída!")

        cv.destroyWindow(window_name)

        return self.cte

    def __click_event(self, event, x, y, flags, param):
        if event != cv.EVENT_LBUTTONDOWN:
            return

        print(f"Ponto selecionado: {x}, {y}")

        self.uv_points.append([x, y])
        # Fecha a janela de seleção de cor

    def __coef_calc(self):
        # Montando a matriz A
        uvarray = np.array(self.uv_points)
        uvec = uvarray[:, 0][:, np.newaxis]
        vvec = uvarray[:, 1][:, np.newaxis]
        A = np.block([np.ones((len(self.xy_points), 1)), uvarray, (uvec**2),
                     (vvec**2)])

        # Montando as matrizes B
        Bx = np.array(self.xy_points)[:, 0][:, np.newaxis]
        By = np.array(self.xy_points)[:, 1][:, np.newaxis]

        # Calculando a pseudo-inversa
        A_ = np.linalg.inv(A.T@A)@A.T

        # Calculando os coeficientes
        alpha = (A_@Bx).T
        beta = (A_@By).T

        return alpha[0], beta[0]


# def select_teams():
#     orange, blue, green, pink, yellow = Color('laranja'), Color('azul'), \
#         Color('verde'), Color('rosa'), Color('amarelo')
#     # team1 = Team(100.0, blue, pink, yellow)
#     # team2 = Team(100.0, green, pink, yellow)
#     # return team1, team2


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
        self.lower_hsv = None
        self.upper_hsv = None
        self.uv = None

        self.select()

    def select(self):
        global cap, frame, waitKey_delay

        window_name = f"Clique na cor desejada para '{self.name}'"
        cv.namedWindow(window_name)

        try:
            while self.lower_hsv is None and self.upper_hsv is None:
                ret, frame = cap.read()

                if not ret:
                    # raise RuntimeError("Falha ao capturar o frame da câmera.")
                    # HACK: reiniciar o vídeo quando ele chega ao fim
                    cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # rascunho
                    print('Rewinding video...')  # rascunho
                    continue  # rascunho

                frame_enhanced = enhance_contrast(frame)
                cv.imshow(window_name, frame_enhanced)
                cv.setMouseCallback(window_name, self.__click_event,
                                    param=frame_enhanced)
                key = cv.waitKey(waitKey_delay)

                if key == ord('q'):
                    break

        finally:
            cv.destroyWindow(window_name)

        frame_hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(frame_hsv, self.lower_hsv, self.upper_hsv)
        frame_hsv_masked = cv.bitwise_and(frame_hsv, frame_hsv, mask=mask)
        res = cv.cvtColor(frame_hsv_masked, cv.COLOR_HSV2BGR)

        window_name = "Isolamento da cor selecionada"
        cv.imshow(window_name, res)
        cv.waitKey(0)
        cv.destroyWindow(window_name)

    def __click_event(self, event, x, y, flags, param):
        '''
        @param param: é a imagem passada quando a função de callback é chamada
        '''
        if event != cv.EVENT_LBUTTONDOWN:
            return

        clicked_color = param[y, x]
        # print(f'clicked_color = {clicked_color}')  # rascunho

        # Converte a cor clicada de BGR para HSV
        hsv_color = cv.cvtColor(
            np.uint8([[clicked_color]]), cv.COLOR_BGR2HSV)[0][0]
        # print(f'hsv_color = {hsv_color}')  # rascunho
        # print(f'np.clip = {np.clip(hsv_color[1] + self.hs_tolerance[1], 0, 255)}')  # rascunho

        lower_h = int(hsv_color[0]) - self.hs_tolerance[0]
        lower_s = int(hsv_color[1]) - self.hs_tolerance[1]
        # print(f'lower_h = {lower_h}')  # rascunho
        # print(f'lower_s = {lower_s}')  # rascunho
        self.lower_hsv = np.array([
            np.clip(lower_h, 0, 179),
            np.clip(lower_s, 0, 255),
            20
        ])

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

            M = cv.moments(contour)

            if M["m00"] == 0:
                continue

            uv = (int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"]))
            print(f'cor {self.name}: uv = {uv} | área = {area}')  # rascunho

            if multi_centroids:
                self.uv.append(uv)
            else:
                self.uv = uv
                break

        return self.uv


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

    def find_pose(self, frame_hsv):
        global frame

        # HACK: tenta encrontrar todos os centroides da cor do time com área
        # igual ou maior que a área mínima. Com isso, é feito um ROI para cada
        # centroide do time, para tentar encontrar a cor do player (cor do
        # círculo).

        self.team_color.find_centroid(frame_hsv, multi_centroids=True)

        for team_centroid in self.team_color.uv:
            roi_hsv = self.__get_roi(frame_hsv, team_centroid)
            self.player_color.find_centroid(roi_hsv)

            if self.player_color.uv is not None:
                self.team_color.uv = team_centroid
                break

        # TODO: transformar o centroide do ROI para o centroide do frame
        # TODO: verificar se o 'pose' está realmente correto

        if self.player_color.uv is None:
            self.pose = {'x': None, 'y': None, 'theta': None}
        else:
            rx, ry = uv_to_xy(team_centroid, self.cte)
            theta_rad = self.__get_theta()

            self.pose['x'] = rx - (self.xoff * np.cos(theta_rad))
            self.pose['y'] = ry + (self.xoff * np.sin(theta_rad))
            self.pose['theta'] = np.degrees(theta_rad)

            cv.circle(frame, self.team_color.uv, 3, (0, 0, 255), -1)
            text = f"(u,v) = {self.team_color.uv}"
            cv.putText(frame, text, self.team_color.uv, cv.FONT_HERSHEY_PLAIN,
                       1, (255, 255, 0), 1)

        return self.pose

    def __get_roi(self, frame_hsv, uv):
        # Limites verticais (linhas - coordenada v)
        v_start = max(0, uv[1] - self.roi_sz)
        v_end = min(frame.shape[0], uv[1] + self.roi_sz)

        # Limites horizontais (colunas - coordenada u)
        u_start = max(0, uv[0] - self.roi_sz)
        u_end = min(frame.shape[1], uv[0] + self.roi_sz)

        # Extração da região de interesse (ROI) na imagem HSV
        return frame_hsv[v_start:v_end, u_start:u_end]

    def __get_theta(self):
        # Diferença entre as coordenadas verticais (v)
        delta_v = self.player_color.uv[1] - self.team_color.uv[1]

        # Diferença entre as coordenadas horizontais (u)
        delta_u = self.player_color.uv[0] - self.team_color.uv[0]

        # Calcula o ângulo em radianos usando arctan2
        theta_rad = -np.arctan2(delta_v, delta_u)  # TODO: verificar se tem o sinal de menos mesmo

        return theta_rad


class Ball:
    def __init__(self, color, cte):
        self.color = color
        self.pose = {'x': None, 'y': None}
        self.cte = cte

    def find_pose(self, frame_hsv):
        global frame

        self.color.find_centroid(frame_hsv)

        if self.color.uv is None:
            print('Ball not found')
            return

        rx, ry = uv_to_xy(self.color.uv, self.cte)

        cv.circle(frame, self.color.uv, 3, (255, 0, 0), -1)
        # text = f"ball (u,v) = {self.color.uv}"
        text = f"ball (x,y) = {rx},{ry}"
        cv.putText(frame, text, self.color.uv, cv.FONT_HERSHEY_PLAIN, 1,
                   (255, 255, 0), 1)


def main():
    global cap, frame, waitKey_delay, XY_POINTS

    init_capture()

    window_name = "frame"
    cv.namedWindow(window_name)

    calib = Calibration(XY_POINTS)
    calib.select_points()

    # green = Color('verde')
    # pink = Color('rosa', min_area=0)
    orange = Color('laranja', min_area=50, hs_tolerance=(5, 75))

    # robot = Robot(green, pink, calib.cte)
    ball = Ball(orange, calib.cte)

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                # raise RuntimeError("Falha ao capturar o frame da câmera.")
                # HACK: reiniciar o vídeo quando ele chega ao fim
                cap.set(cv.CAP_PROP_POS_FRAMES, 0)  # rascunho
                print('Rewinding video...')  # rascunho
                continue  # rascunho

            frame_enhanced = enhance_contrast(frame)
            frame_hsv = cv.cvtColor(frame_enhanced, cv.COLOR_BGR2HSV)

            # robot.find_pose(frame_hsv)
            ball.find_pose(frame_hsv)

            cv.imshow(window_name, frame)
            key = cv.waitKey(waitKey_delay)

            if key == ord('q'):
                break

    finally:
        cv.destroyWindow(window_name)
        cap.release()


if __name__ == '__main__':
    main()
