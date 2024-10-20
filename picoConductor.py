import time
import network
import uasyncio as asyncio
from BLE_CEEO import Yell
from mqtt import MQTTClient
from machine import ADC, Pin

from Conductor import Conductor # Class to control the tune
from secrets import mysecret, key

# ------ CREATING AND CONNECTING MIDI CONDUCTOR ------
midi = Yell('frog', verbose = True, type = 'midi')
conductor = Conductor(midi)
conductor.connect()

# ------ MQTT SET UP ------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(mysecret, key)
    while not wlan.isconnected():
        time.sleep(1)
    print('----- connected to wifi -----')
        
# ------ CONNECTING UP MQTT -------
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/linuslucy' # goal is to play linus and lucy!

async def callback(topic, msg):
    global conductor
    
    val = msg.decode()
    print("MQTT Message received: "+val)
    
    # Listening for start/stop commands from light sensor
    if val == 'start':
        conductor.turnOn()
        print("CALLBACK - STARTING")
        
    elif val == 'stop':
        conductor.turnOff()
        print("CALLBACK - STOPPING")

    # Listening for MQTT from the accelerometer data
    elif val[0] == 'T':
        await conductor.changeTempo(float(val[1:]))
        print("CALLBACK - CHANGED TEMPO TO: "+str(val[1:]))

connect_wifi()
client = MQTTClient('AnnePico', mqtt_broker, port, keepalive=60)
client.set_callback(lambda topic, msg: asyncio.create_task(callback(topic,msg)))
client.connect()
client.subscribe(topic_sub.encode())
print(f'Subscribed to {topic_sub}')

# ---- HANLER FUNCTIONS------
def connect_mqtt(client):
    client.connect()
    client.subscribe(topic_sub.encode())
    print(f'Subscribed to {topic_sub}')
    
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

# ---- PHOTORESISTOR PAUSE FUNCTION ------
lightSensor = Pin('GPIO26')

async def lightPauseButton(pin):
    photoRes = ADC(pin)
    
    while True:
        light = photoRes.read_u16()
        light = round(light/65535*100,2)
        
        if light < 15:
            print("light covered: " + str(light) + "%")
            conductor.turnOff()
        if light > 15 and not conductor.checkState():
            conductor.turnOn()
        await asyncio.sleep(0.01)
    

# ----- RUNNING ASYNC FUNCTIONS -----
loop = asyncio.get_event_loop()
loop.create_task(mqtt_handler(client))
loop.create_task(conductor.handler())
loop.create_task(lightPauseButton(lightSensor))
loop.run_forever()
