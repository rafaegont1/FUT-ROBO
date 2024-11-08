import paho.mqtt.client as mqtt
import time

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f'Connected with result code {reason_code}')
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('testeesp32-pc')

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+msg.payload.decode('utf-8'))

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, 'PC')
client.on_connect = on_connect
client.on_message = on_message

client.connect('test.mosquitto.org', 1883)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_start()

while True:
    client.publish('testeesp32-pc', 'Teste Fut-robo')
    time.sleep(1)
    print('Publicado!')