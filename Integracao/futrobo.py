#importando as bibliotecas necessárias:
import numpy as np
import paho.mqtt.client as mqtt
import time
import threading
#from viscomp import *

#Travamento do acesso para evitar erros decorrentes de tentativas de acesso simultâneo entre as threads:
mutex = threading.Lock()

# while True:
#     video.update_frame()
#     poses = viscomp.find_poses(video.frame, video.frame_hsv)
#     print(f"poses = {poses}")

#     key = video.show_frame()

#Thread de visão computacional:
#def th1(self):
    #while(self.loop):
        #Obtendo as poses do robô:

        #Atualiza as poses e envia ao robô:
        # with mutex:
        #     self.AA = praa
        #     self.AR = prar
        #     self.VA = prva
        #     self.VR = prvr
        #     self.client.publish('PCPY-VIS', f'{int(self.AA[0])},{int(self.AA[1])},{int(self.AA[2])},')

#Classe para enviar comandos ao robô:
class ROBO:
    #Contrutor para inicialização da classe e da conexão com o robô:
    def __init__(self, host, port):
        #Configurando o cliente e conectando via MQTT:
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 'PC')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port)
        self.client.loop_start()
        time.sleep(1)
        #Definindo variáveis globais do robô:
        self.loop = True
        self.moving = False
        self.kicking = False
        self.AA = []
        self.AR = []
        self.VA = []
        self.VR = []
        
        #Declarando e iniciando a thread de visão:
        #task1 = threading.Thread(target=th1, args=(self,))
        #Iniciando as threads:
        #task1.start()
    
    #Função de callback executada quando a conexão for estabelecida:
    def on_connect(self, client, userdata, flags, reason_code, properties):
        #Mensagem de status da conexão:
        print(f'Connected with result code {reason_code}')
        #Inscrevendo nos tópicos:
        self.client.subscribe('ESP32-COM', 2)

    #Função de callback executada ao receber uma mensagem:
    def on_message(self, client, userdata, msg):
        #print(msg.topic+" "+msg.payload.decode('utf-8'))
        #Atribuição do valor recebido à variável correspondente:
        with mutex:
            if(msg.topic == 'ESP32-COM'):
                if(msg.payload.decode('utf-8') == 'K1'):
                    self.kicking = False
                if(msg.payload.decode('utf-8') == 'L1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'R1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'G1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'A1'):
                    self.moving = False
    
    #Função para chutar:
    def kick(self, power=100):
        if((power>0) and (power<=100)):
            self.client.publish('PCPY-COM', f'K{int(power)}', 2)
            self.kicking = True
    
    #Funções para movimentação:
    def moveLinear(self, ds, power=100):
        self.client.publish('PCPY-COM', f'L{int(ds)},{int(power)},', 2)
        self.moving = True
    
    def rotate(self, dth, power=100):
        self.client.publish('PCPY-COM', f'R{int(dth)},{int(power)},', 2)
        self.moving = True

    def gotoPos(self, x, y, power=100):
        self.client.publish('PCPY-COM', f'G{int(x)},{int(y)},{int(power)},', 2)
        self.moving = True

    def align(self, th, power=100):
        self.client.publish('PCPY-COM', f'A{int(th)},{int(power)},', 2)
        self.moving = True
    
    #Função para aguardar a movimentação:
    def waitMove(self):
        while(True):
            time.sleep(10e-3)
            if(not self.moving):
                break
    
    #Função para aguardar o chute:
    def waitKick(self):
        while(True):
            time.sleep(10e-3)
            if(not self.kicking):
                break

    #Função para encerrar o programa (fechar as threads, etc...):
    def endProgram(self):
        with mutex:
            self.loop = False
        

#rd = ROBO('test.mosquitto.org', 1883)
rd = ROBO('192.168.137.1', 1884)

#rd.moveLinear(1000)

# time.sleep(4)

# rd.rotate(120, 40)

# time.sleep(2)

# rd.moveLinear(1500)

# time.sleep(4)

# rd.rotate(30, 40)

# time.sleep(2)

rd.kick(100)

time.sleep(1)