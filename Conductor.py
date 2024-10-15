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
        self.isPlaying = False
    
    def turnOn(self):
        self.isOn = True
        print(" ~~~~~~ from conductor: turnOn() ~~~~~")
        
    def turnOff(self):
        self.isOn = False
        print(" ~~~~~~ from conductor: turnOff() ~~~~~")
    
    def startPlay(self):
        self.isPlaying = True

    def connect(self):
        self.midi.connect_up()
        
    def disconect(self):
        self.midi.disconnect()
        
    def playTune(self):
        print(" ~~~~~~ from conductor: playTune() ~~~~~")
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
        payload = bytes([tsM,tsL,c,note,velocity['f']])

        
        # Defining the tune!!!!
        notesRightHand = [
            (74, 64),
            (79,64)
        ]
        
        notesLeftHand = [
            (38, 64),
            (36, 64),
            (38, 32),
            (36, 32)
        ]
        
        
        # ------- Playing the tune -----
        for note, duration in notesLeftHand:
            # note on
            payload = bytes([tsM,tsL,c,note,velocity['f']])
            self.midi.send(payload)
            time.sleep(duration/1000)
            
        
    async def handler(self):
        print(" ~~~~~~ from conductor: handler() ~~~~~")
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
        payload = bytes([tsM,tsL,c,note,velocity['f']])
    
        # Notes:
        # 64 = quarter note
        # 32 = eight note
        # am working in Octave 2 and Octave 3
        melody = [
            (48, 32), # measure 1
            (50, 32),
            (52, 64),
            (52, 32),
            (50, 32),
            (48, 64),
            (50, 96),# measure 2
            (48, 160),
            (48, 32), #measure 3
            (50, 32),
            (52, 64),
            (52, 384), # measure 3+4
            (48, 32), # measure 5
            (50, 32),
            (52, 64),
            (52, 32),
            (50, 32),
            (48, 64),
            (50, 96), # measure 6
            (48, 160),
            (48, 96), # measure 7
            (50, 32),
            (50, 384), # measure 7 + 8
            (48, 96), # measure 9
            (50, 32),
            (50, 384), # measure 10 + 11
            (79, 64),
            (79, 64)
        ]
        
        notesLeftHand = [
            (38, 64),
            (36, 64),
            (38, 32),
            (36, 32)
        ]
        
        while True:
            if self.isOn and not self.isPlaying:
                self.isPlaying = True
                print("starting tune")
                
                # start notes
                for note in melody:
    
                    if self.isOn:
                        payload = bytes([tsM,tsL,c,note[0],velocity['f']])
                        self.midi.send(payload)
                        await asyncio.sleep(note[1]/100)
                        
                        payloadOff = bytes([tsM,tsL,c,note[0],0])
                        self.midi.send(payloadOff)
                    else:
                        self.pauseIndex = note
                        break
                self.isPlaying = False
                print("ending tune")
                
                    
                    
            await asyncio.sleep(0.01)
            
        
        

