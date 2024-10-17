from machine import Pin, SoftI2C, PWM, ADC
from mqtt import MQTTClient
import network
import time
import uasyncio as asyncio
import servo
import ssd1306
import adxl345

from secrets import mysecret, key
    
# ----- TEST CODE ------
i2c = SoftI2C(scl = Pin(7), sda = Pin(6))

screen = ssd1306.SSD1306_I2C(128,64,i2c)
screen.text('Hello World', 0, 0, 1) # to display text
screen.show()

adx = adxl345.ADXL345(i2c)
#print(adx.xValue)

pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB) # the pin expects a voltage range up to 3.3V
#print(pot.read()) #range 0-4095

motor = servo.Servo(Pin(2)) 
#motor.write_angle(90) # - to turn the motor to 30 degrees

sd = Pin(8, Pin.IN)
sd.value()


# ------ MQTT SUBSCRIBER SET UP ------
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/linuslucy'

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

def sendMessage():
    global screen
    print("inside sendMessage()")
    screen.fill(0)
    screen.text('Good Grief ._.', 0, 0, 1) # to display text
    screen.show()
    
def callback(topic, msg):
    global conductor
    
    val = msg.decode()
    print("MQTT Message received: "+val)

    if val == 'msg':
        sendMessage()

        
    
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
        
# ------ CONNECTING UP MQTT -------
# After midi bluetooth keyboard is set up, start handling MQTT 
connect_wifi()
client = MQTTClient('ME35_linuslucy2', mqtt_broker, port, keepalive=60)
client.set_callback(callback)
client.connect()
client.subscribe(topic_sub.encode())
print(f'Subscribed to {topic_sub}')

# ----- RUNNING ASYNC FUNCTIONS -----
loop = asyncio.get_event_loop()
loop.create_task(mqtt_handler(client))
loop.run_forever()

