import cv2 as cv
from src.color import Color
from src.publisher import Publisher
from src.calibration import uv_to_xy


class Ball:
    def __init__(self, color, cte):
        self.color = color
        self.pose = [None, None]
        self.cte = cte

        # self.pub = Publisher('ball')

    # Função de callback para quando a conexão for bem-sucedida
    def __on_connect(self, client, userdata, flags, rc):
        print(f"Conectado com código {rc}")

    # Função de callback para quando a publicação for confirmada
    def __on_publish(self, client, userdata, mid):
        print(f"Mensagem publicada com id: {mid}")

    def find_pose(self, frame, frame_hsv):
        self.color.find_centroid(frame_hsv)

        if self.color.uv is None:
            print('Ball not found')
            return

        self.pose[0], self.pose[1] = uv_to_xy(self.color.uv, self.cte)

        cv.circle(frame, self.color.uv, 3, (255, 0, 0), -1)
        # text = f"ball (u,v) = {self.color.uv}"
        text = f"ball {self.pose[0]},{self.pose[1]}"
        cv.putText(frame, text, self.color.uv, cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)

        # self.pub.publish(self.pose.values())
        # Transformando os valores (floats) em inteiros e, em seguida, criando a string
        # msg = ', '.join(map(lambda x: str(int(x)), self.pose.values()))
        # self.client.publish('ball', msg)

        return self.pose
