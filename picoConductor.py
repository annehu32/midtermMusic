import time
import network
import uasyncio as asyncio
from BLE_CEEO import Yell
from mqtt import MQTTClient
from machine import Pin, PWM # not in use yet...
from secrets import mysecret, key

# ------ CREATING A CONDUCTOR ------
# Pico should connect before handilng MQTT requests because this requires manual input from the Mac user
midi = Yell('frog', verbose = True, type = 'midi')

from Conductor import Conductor # Class to control the tune
conductor = Conductor(midi)
conductor.connect()

# ------ MQTT SET UP ------
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/linuslucy' # goal is to play linus and lucy!
isOn = False # tracking MQTT commands

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(mysecret, key)
    while not wlan.isconnected():
        time.sleep(1)
    print('----- connected to wifi -----')
    
def connect_mqtt(client):
    client.connect()
    client.subscribe(topic_sub.encode())
    print(f'Subscribed to {topic_sub}')
    
def callback(topic, msg):
    global conductor
    
    val = msg.decode()
    print("MQTT Message received: "+val)
    
    if val == 'start':
        conductor.turnOn()
        print("CALLBACK - STARTING")
    elif val == 'stop':
        conductor.turnOff()
        print("CALLBACK - STOPPING")
    elif val == 'bye':
        conductor.disconnect()
        print("CALLBACK - DISCONNECTING")
    
async def mqtt_handler(client):
    while True:
        if network.WLAN(network.STA_IF).isconnected():
            try:
                client.check_msg()
            except Exception as e:
                print('MQTT callback failed')
                connect_mqtt(client)
        else:
            print('Wifi disconnected, trying to connect...')
            connect_wifi()
        await asyncio.sleep(0.01)

# ------ MAIN CODE ------
async def main():
    global isOn
    global midi
    
    
    
    while True:
        if isOn:
            print("----- IN NOTE LOOP ----- ")
            for i in range(5):
                midi.send(payload)
            asyncio.sleep(5)
        else:
            print("--- Waiting for start command ---")
        await asyncio.sleep(0.01)
        
        

# ------ CONNECTING UP MQTT -------
# After midi bluetooth keyboard is set up, start handling MQTT 
connect_wifi()
client = MQTTClient('ME35_linuslucy', mqtt_broker, port, keepalive=60)
client.set_callback(callback)
client.connect()
client.subscribe(topic_sub.encode())
print(f'Subscribed to {topic_sub}')

# ----- RUNNING ASYNC FUNCTIONS -----
loop = asyncio.get_event_loop()
loop.create_task(mqtt_handler(client))
loop.create_task(conductor.handler())
#loop.create_task(main())
loop.run_forever()
