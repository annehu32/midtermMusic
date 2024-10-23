import time
import network
import uasyncio as asyncio
from BLE_CEEO import Yell
from mqtt import MQTTClient
from machine import Pin, PWM # not in use yet...
from secrets import mysecret, key

class Conductor():

    # Initializer takes midi object
    def __init__(self, midiBluetooth):
        self.midi = midiBluetooth
        
        self.masterOn = False
        self.isOn = False
        
        self.tempo = 1.5
        self.vol = 'f'
        
        self.client = None
        self.topic_pub = 'ME35-24/linuslucydahal'
        
        print("----- conductor successfully instantiated------")
    
    # ------ MQTT SET UP ------
    def connect_wifi(self):
        from secrets import mysecret, key
        
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(mysecret, key)
        while not wlan.isconnected():
            time.sleep(1)
        print('----- Conductor object is connected to wifi -----')
        
    def createClient(self):
        self.connect_wifi()
        
        mqtt_broker = 'broker.hivemq.com'
        port = 1883

        self.client = MQTTClient('ConductorObject', mqtt_broker, port, keepalive=120)
        self.client.connect()
        print("Conductor object has created a client!!!")
    
    # ------- HELPER FUNCTIONS --------
    async def turnMasterOn(self):
        self.masterOn  = True
        await asyncio.sleep(0.01)
        print(" ~~~~~~ from conductor: masterOn() ~~~~~")
        
    async def turnMasterOff(self):
        self.masterOn = False
        await asyncio.sleep(0.01)
        print("~~~~~~ from conductor: masterOff() ~~~~~")
        
    def turnOn(self):
        self.isOn = True
        print(" ~~~~~~ from conductor: turnOn() ~~~~~")
        
    def turnOff(self):
        self.isOn = False
        print(" ~~~~~~ from conductor: turnOff() ~~~~~")
    
    async def changeTempo(self, val):
        self.tempo = float(val)
        print("-------- TEMPO CHANGED!!!!! -------")
        print(" ------- " + str(self.tempo)+ " ----------")
        await asyncio.sleep(0.01)
    
    def changeVol(self, val):
        #val must be input as one of the corresponding velocity options
        self.vol = val
    
    def getTempo(self):
        return self.tempo

    def connect(self):
        self.midi.connect_up()
        
    def disconect(self):
        self.midi.disconnect()
    
    def checkState(self):
        return self.isOn
        
    async def handler(self):
        # ----- MIDI SETUP ------
        NoteOn = 0x90
        NoteOff = 0x80
        StopNotes = 123
        SetInstroment = 0xC0
        Reset = 0xFF

        velocity = {'off':0, 'pppp':8,'ppp':20,'pp':31,'p':42,'mp':53,
            'mf':64,'f':80,'ff':96,'fff':112,'ffff':127}
        
        channel = 0
        note = 55
        cmd = NoteOn
        
        channel = 0x0F & channel
        timestamp_ms = time.ticks_ms()
        tsM = (timestamp_ms >> 7 & 0b111111) | 0x80
        tsL =  0x80 | (timestamp_ms & 0b1111111)

        c =  cmd | channel     
        payload = bytes([tsM,tsL,c,note,velocity[self.vol]])
        from song import melody
     
        while True:
            # At beginning of song, have servo move
            msg = 'spin'
            try:
                self.client.publish(self.topic_pub.encode(), msg.encode())
                print("Sent spin message to Dahal Board")
            except Exception as e:
                self.client.connect()
                print("Reconnected, trying again...")
                self.client.publish(self.topic_pub.encode(), msg.encode())


            # For each note in song, make sure light uncovered, then play
            for i in range(0, len(melody)):
                temp = self.getTempo()
                print("----- tempo is: "+str(temp)+" --------")

                print("----- Note index: "+str(i)+" --------")
                note = melody[i]
                
                while not self.masterOn:
                    print("------ Master key is off --------")
                    await asyncio.sleep(0.01)
                
                while not self.isOn:
                    print(" ------- Waiting for go on note #: "+str(i)+" --------")
                    await asyncio.sleep(0.01)
                
                # When isOn, will play the note
                payload = bytes([tsM,tsL,c,note[0],velocity[self.vol]])
                self.midi.send(payload)
                
                await asyncio.sleep(note[1]/(temp*100))
                
                payloadOff = bytes([tsM,tsL,c,note[0],0])
                self.midi.send(payloadOff)
                    
            await asyncio.sleep(0.01)
