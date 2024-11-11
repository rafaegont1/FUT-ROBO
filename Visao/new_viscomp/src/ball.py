import cv2 as cv
import paho.mqtt.client as mqtt
from src.color import Color
from src.calibration import uv_to_xy

class Ball:
    def __init__(self, color, cte):
        self.color = color
        self.pose = {'x': None, 'y': None}
        self.cte = cte

        self.client = mqtt.Client()
        # Definir os callbacks
        self.client.on_connect = self.__on_connect
        self.client.on_publish = self.__on_publish
        # Conectar ao broker MQTT
        self.client.connect('broker.emqx.io', 1883)
        # Iniciar o loop do cliente para manter a conexão ativa
        self.client.loop_start()  # Usando loop_start() para não bloquear a execução do código

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

        self.pose['x'], self.pose['y'] = uv_to_xy(self.color.uv, self.cte)

        cv.circle(frame, self.color.uv, 3, (255, 0, 0), -1)
        # text = f"ball (u,v) = {self.color.uv}"
        text = f"ball (x,y) = {self.pose['x']},{self.pose['y']}"
        cv.putText(frame, text, self.color.uv, cv.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), 1)

        # Transformando os valores (floats) em inteiros e, em seguida, criando a string
        msg = ', '.join(map(lambda x: str(int(x)), self.pose.values()))
        self.client.publish('ball', msg)
