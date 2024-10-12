import time
import network
import uasyncio as asyncio
from BLE_CEEO import Yell
from mqtt import MQTTClient
from machine import Pin, PWM # not in use yet...
from secrets import mysecret, key


# ------ MQTT SET UP ------
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/linuslucy' # goal is to play linus and lucy!

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
    val = msg.decode()
    print("MQTT Message received: "+val)
    
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

# ------ MIDI SET UP ------
NoteOn = 0x90
NoteOff = 0x80
StopNotes = 123
SetInstroment = 0xC0
Reset = 0xFF

velocity = {'off':0, 'pppp':8,'ppp':20,'pp':31,'p':42,'mp':53,
    'mf':64,'f':80,'ff':96,'fff':112,'ffff':127}

# ------ CONNECTING UP BLUETOOTH ------
connect_wifi()

p = Yell('frog', verbose = True, type = 'midi')
p.connect_up()
        
channel = 0
note = 55
cmd = NoteOn

channel = 0x0F & channel
timestamp_ms = time.ticks_ms()
tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
tsL =  0x80 | (timestamp_ms & 0b1111111)

c =  cmd | channel     
payload = bytes([tsM,tsL,c,note,velocity['f']])

for i in range(5):
    p.send(payload)
    time.sleep(5)
p.disconnect()
