import paho.mqtt.client as mqtt


class Publisher:
    def __init__(self, topic):
        self.topic = topic

        self.client = mqtt.Client()

        self.client.on_connect = self.__on_connect
        self.client.on_publish = self.__on_publish

        self.client.connect('broker.emqx.io', 1883)

        self.client.loop_start()

    def publish(self, data):
        msg = ', '.join(str(int(x)) for x in data)
        self.client.publish(self.topic, msg)

    def __on_connect(self, client, userdata, flags, rc):
        print(f"Conectado com código {rc}")

    def __on_publish(self, client, userdata, mid):
        print(f"Mensagem publicada com id: {mid}")
