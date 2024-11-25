#importando as bibliotecas necessárias:
import numpy as np
import paho.mqtt.client as mqtt
import time
import threading

#Travamento do acesso para evitar erros decorrentes de tentativas de acesso simultâneo entre as threads:
mutex = threading.Lock()

#Thread de visão computacional:
# def th1(self):
#     while(self.loop):
#         if(self.move):
#             if(True):
#             #if(abs(np.sqrt((self.target[0]**2)+(self.target[1]**2))-(self.sd-self.sd0))>5):
#                 #print(self.sd)
#                 #Lógica de controle:
#                 vd = 80
#                 ve = 0
#                 #Envia os setpoints de velocidade para os motores:
#                 rc,_ = self.client.publish('pcpy-refd', str(vd))
#                 #print(mqtt.error_string(rc))
#                 self.client.publish('pcpy-refe', str(ve))
#             else:
#                 self.client.publish('pcpy-refd', str(0))
#                 self.client.publish('pcpy-refe', str(0))
#                 self.move = False
#         time.sleep(1)

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
        
        # #Declarando as threads:
        # task1 = threading.Thread(target=th1, args=(self,))
        # #Iniciando as threads:
        # task1.start()
    
    #Função de callback executada quando a conexão for estabelecida:
    def on_connect(self, client, userdata, flags, reason_code, properties):
        #Mensagem de status da conexão:
        print(f'Connected with result code {reason_code}')
        #Inscrevendo nos tópicos:
        self.client.subscribe('ESP32-COM')

    #Função de callback executada ao receber uma mensagem:
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+msg.payload.decode('utf-8'))
        #Atribuição do valor recebido à variável correspondente:
        with mutex:
            if(msg.topic == 'ESP32-COM'):
                if(msg.payload.decode('utf-8') == 'K1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'L1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'R1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'G1'):
                    self.moving = False
                if(msg.payload.decode('utf-8') == 'A1'):
                    self.moving = False
    
    #Função para chutar:
    def kick(self, power):
        self.client.publish('PCPY-COM', f'K{power}')
        self.kicking = True
    
    #Funções para movimentação:
    def moveLinear(self, ds, power):
        with mutex:
            self.client.publish('PCPY-COM', f'G{int(ds)},{int(power)}')
            self.moving = True
    
    def rotate(self, dth, power):
        with mutex:
            self.client.publish('PCPY-COM', f'G{int(dth)},{int(power)}')
            self.moving = True

    def gotoPos(self, x, y, power):
        with mutex:
            self.client.publish('PCPY-COM', f'G{int(x)},{int(y)},{int(power)}')
            self.moving = True

    def align(self, th, power):
        with mutex:
            self.client.publish('PCPY-COM', f'G{int(th)},{int(power)}')
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
        self.loop = False
        

rd = ROBO('test.mosquitto.org', 1883)

#rd.moveLinear(500, 100)

rd.kick(100)