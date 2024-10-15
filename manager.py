#importando as bibliotecas necessárias:
import numpy as np
import paho.mqtt.client as mqtt
import time
import threading

#Travamento do acesso para evitar erros decorrentes de tentativas de acesso simultâneo entre as threads:
mutex = threading.Lock()

#Thread de movimentação do robô:
def th1(self):
    while(self.loop):
        if(self.move):
            if(True):
            #if(abs(np.sqrt((self.target[0]**2)+(self.target[1]**2))-(self.sd-self.sd0))>5):
                #print(self.sd)
                #Lógica de controle:
                vd = 80
                ve = 0
                #Envia os setpoints de velocidade para os motores:
                rc,_ = self.client.publish('pcpy-refd', str(vd))
                #print(mqtt.error_string(rc))
                self.client.publish('pcpy-refe', str(ve))
            else:
                self.client.publish('pcpy-refd', str(0))
                self.client.publish('pcpy-refe', str(0))
                self.move = False
        time.sleep(1)

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
        #Definindo variáveis globais do robô:
        self.loop = True
        self.kicking = False
        self.free_front = True
        self.dd = 300
        self.dc = 300
        self.de = 300
        self.refd = 0
        self.refe = 0
        self.sd = 0
        self.se = 0
        self.vd = 0
        self.ve = 0
        self.ed = 0
        self.ee = 0
        self.ud = 0
        self.ue = 0
        self.sd0 = 0
        self.se0 = 0
        self.move = False
        self.target = [0,0]
        #Declarando as threads:
        task1 = threading.Thread(target=th1, args=(self,))
        #Iniciando as threads:
        task1.start()
        #Habilita o controle remoto:
        self.client.publish('pcpy-rc', str(1))
    
    #Função de callback executada quando a conexão for estabelecida:
    def on_connect(self, client, userdata, flags, reason_code, properties):
        #Mensagem de status da conexão:
        print(f'Connected with result code {reason_code}')
        #Inscrevendo nos tópicos:
        self.client.subscribe('esp32-kstate')
        self.client.subscribe('esp32-ca')
        self.client.subscribe('esp32-dd')
        self.client.subscribe('esp32-dc')
        self.client.subscribe('esp32-de')
        self.client.subscribe('esp32-refd')
        self.client.subscribe('esp32-refe')
        self.client.subscribe('esp32-sd')
        self.client.subscribe('esp32-se')
        self.client.subscribe('esp32-vd')
        self.client.subscribe('esp32-ve')
        self.client.subscribe('esp32-ed')
        self.client.subscribe('esp32-ee')
        self.client.subscribe('esp32-ud')
        self.client.subscribe('esp32-ue')

    #Função de callback executada ao receber uma mensagem:
    def on_message(self, client, userdata, msg):
        #print(msg.topic+" "+msg.payload.decode('utf-8'))
        #Atribuição do valor recebido à variável correspondente:
        with mutex:
            if(msg.topic == 'esp32-kstate'):
                self.kicking = bool(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ca'):
                self.free_front = bool(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-dd'):
                self.dd = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-dc'):
                self.dc = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-de'):
                self.de = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-refd'):
                self.refd = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-refe'):
                self.refe = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-sd'):
                self.sd = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-se'):
                self.se = int(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-vd'):
                self.vd = float(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ve'):
                self.ve = float(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ed'):
                self.ed = float(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ee'):
                self.ee = float(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ud'):
                self.ud = float(msg.payload.decode('utf-8'))
            if(msg.topic == 'esp32-ue'):
                self.ue = float(msg.payload.decode('utf-8'))
    
    #Função para chutar:
    def kick(self, power):
        self.client.publish('pcpy-kick', str(power))
        time.sleep(0.5)
    
    #Função para movimentação:
    def gotoPos(self, x,y):
        with mutex:
            self.target = [x,y]
            self.sd0 = self.sd
            self.se0 = self.se
            self.move = True
    
    #Função para aguardar a movimentação:
    def waitMove(self):
        while(True):
            time.sleep(10e-3)
            if(not self.move):
                break

    #Função para encerrar o programa (fechar as threads, etc...):
    def endProgram(self):
        self.loop = False
        #Desabilita o controle remoto:
        self.client.publish('pcpy-rc', str(0))
        

rd = ROBO('test.mosquitto.org', 1883)

rd.gotoPos(200, 200)

rd.waitMove()

#rd.kick(100)

rd.endProgram()