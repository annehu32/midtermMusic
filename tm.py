#Code to run on PC for Teachable Machine Joystick
from pyscript.js_modules import teach, pose, ble_library, mqtt_library

#ble = ble_library.newBLE()
myClient = mqtt_library.myClient
mqtt_connected = False
pub_topic = 'ME35-24/linuslucy'

async def run_model(URL2):
    s = teach.s  # or s = pose.s
    s.URL2 = URL2
    await s.init()
    
async def connect(name):
    global mqtt_connected
    myClient.init()
    while not myClient.connected:
        await asyncio.sleep(2)
    mqtt_connected = True

def send(message):
    print('sending ', message)
    myClient.publish(pub_topic, message)

def get_predictions(num_classes):
    predictions = []
    for i in range (0,num_classes):
        divElement = document.getElementById('class' + str(i))
        if divElement:
            divValue = divElement.innerHTML
            predictions.append(divValue)
            print(divValue)
    return predictions

import asyncio
await run_model("https://teachablemachine.withgoogle.com/models/t58WGMjvv/") #Change to your model link
await connect('Anne')

# Handling message sending
threshold = 0.9 
lastMessage = None

while True:
    if mqtt_connected:
        predictions = get_predictions(4)   

        for guess in predictions:
            if guess[:4] == 'lucy':
                print("READING LUCY!!!")
                confidence = float(guess[6:])
                if confidence > threshold and not lastMessage == 'LU':
                    send('LU')
                    lastMessage = 'LU'
            elif guess[:5] =='linus' and not lastMessage == 'LI':
                print("READING LINUS!!!")
                confidence = float(guess[7:])
                if confidence > threshold:
                    send('LI')
                    lastMessage = 'LI'
            elif guess[:6] == 'snoopy' and not lastMessage == 'SN':
                print("READING SNOOPY!!!")
                confidence = float(guess[8:])
                if confidence > threshold:
                    send('SN')
                    lastMessage = 'SN'
        
    await asyncio.sleep(2)
