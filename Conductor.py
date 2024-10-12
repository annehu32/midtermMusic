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
        self.isOn = False
        self.pauseIndex = 0 # For pausing function, want to know at what note were we paused
        print("----- conductor successfully instantiated------")
    
    def turnOn(self):
        self.isOn = True
        print(" ~~~~~~ from conductor: turnOn() ~~~~~")
        
    def turnOff(self):
        self.isOn = False
        print(" ~~~~~~ from conductor: turnOff() ~~~~~")

    def connect(self):
        self.midi.connect_up()
        
    def disconect(self):
        self.midi.disconnect()
        
    async def testTune(self):
        print(" ~~~~~~ from conductor: testTune() ~~~~~")
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
        payload = bytes([tsM,tsL,c,note,velocity['f']])
        
        while True:
            for i in range(5):
                if self.isOn:
                    self.midi.send(payload)
                    asyncio.sleep(5)
            await asyncio.sleep(0.01)
