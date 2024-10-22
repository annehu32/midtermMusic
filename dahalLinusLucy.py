from machine import Pin, SoftI2C, PWM, ADC
from mqtt import MQTTClient
import network
import time
import uasyncio as asyncio
import servo
import ssd1306
import adxl345

from secrets import mysecret, key

# ------ BOARD FUNCTIONS -----
i2c = SoftI2C(scl = Pin(7), sda = Pin(6))
screen = ssd1306.SSD1306_I2C(128,64,i2c)
screen.text('Hello World', 0, 0, 1) # to display text
screen.show()

# Prints a set message to the LCD onboard
def printLinus():
    global screen
    screen.fill(0)
    
    screen.text("There's no" , 0, 0, 1) # to display text
    screen.text("heavier burden", 0, 10, 1) 
    screen.text("than a great", 0, 20, 1)
    screen.text("potential!", 0, 30, 1)
 
    screen.show()

def printLucy():
    global screen
    screen.fill(0)
    
    screen.text("If everyone" , 0, 0, 1) # to display text
    screen.text("listened to me,", 0, 10, 1) 
    screen.text("this would be a", 0, 20, 1)
    screen.text("perfect world!", 0, 30, 1)
 
    screen.show()
    
def printSnoopy():
    global screen
    screen.fill(0)
    
    screen.text("Whatever it is" , 0, 0, 1) # to display text
    screen.text("Snoopy would ", 0, 10, 1) 
    screen.text("say.", 0, 20, 1)
 
    screen.show()
# Prints a given message to the LCD onboard
def printMessage(msg):
    global screen
    screen.fill(0)
    screen.text(msg, 0, 0, 1) # to display text
    screen.show()

# async function to read potentiometer values and send via MQTT
async def readPot(client):    
    # Potentiometer range = 1 -> 4095
    # tempo will range from pot(1) = 1 to pot(4095) = 3
    potMax = 4095 # maximum value read by potentiometer
    pot = ADC(Pin(3))
    pot.atten(ADC.ATTN_11DB) # the pin expects a voltage range up to 3.3V
    lastPub = 1.0

    while True:
        val = pot.read()
        tempo = 1 + 1*(val/potMax)
        
        if abs(lastPub - tempo) > 0.05:
            client.publish(topic_pub, 'T'+str(tempo))
            printMessage("Published: "+str(tempo))
            lastPub = tempo
            
        await asyncio.sleep(0.1) #will be refreshing more slowly than other things for now

#  async function to monitor accelerometer events and send MQTT requests
async def readAcc(client):
    acc = adxl345.ADXL345(i2c)
    accThreshold = 12
    
    while True:
        val = acc.xValue
        mag = abs(val)
        
        if mag > accThreshold:
            print(" Acceleration over threshold ")
            printMessage("Acceleration exceeding threshold")
            client.publish(topic_pub, 'A')
        await asyncio.sleep(3)

# helper function to spin the servo when receive mqtt request
motor = servo.Servo(Pin(2)) 
async def spinServo():
    global motor
    print("in spinServo()")
    motor.write_angle(180) # - to turn the motor to 30 degrees
    await asyncio.sleep(1)
    motor.write_angle(0)
    
    
# ------ MQTT SET UP ------
mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/linuslucydahal'
topic_pub = 'ME35-24/linuslucypico'

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(mysecret, key)
    while not wlan.isconnected():
        time.sleep(1)
    printMessage("wifi connected")

# Helper function to be called if the client somehow gets disconnected
def connect_mqtt(client):
    client.connect()
    client.subscribe(topic_sub.encode())
    printMessage(f'Subscribed: {topic_sub}')

# Handling MQTT subscriptions, need to build this out
async def callback(topic, msg):    
    val = msg.decode()
    print("MQTT received: "+val)

    if val == 'LI':
        printLinus()
    elif val == 'LU':
        printLucy()
    elif val == 'SN':
        printSnoopy()
    elif val == 'spin':
        await spinServo()

async def mqtt_handler(client):
    while True:
        if network.WLAN(network.STA_IF).isconnected():
            try:
                client.check_msg()
            except Exception as e:
                print('MQTT callback failed')
                printMessage('MQTT reconnecting')
                connect_mqtt(client)
        else:
            print('Wifi disconnected, trying to connect...')
            connect_wifi()
        await asyncio.sleep(0.01)
        
# ------ CONNECTING UP MQTT -------
# After midi bluetooth keyboard is set up, start handling MQTT 
connect_wifi()
client = MQTTClient('linusLucyDahal', mqtt_broker, port, keepalive=60)
client.set_callback(lambda topic, msg: asyncio.create_task(callback(topic, msg)))
client.connect()
try:
    client.subscribe(topic_sub.encode())
except Exception as e:
    printMessage('subscribe failed')
printMessage(f'Subscribed to {topic_sub}')

# ----- RUNNING ASYNC FUNCTIONS -----
loop = asyncio.get_event_loop()
loop.create_task(mqtt_handler(client))
loop.create_task(readPot(client))
loop.create_task(readAcc(client))
loop.run_forever()

