import glob
import random, sys
import PyCmdMessenger
import pygame
import time
from time import sleep

hydro_snd = None
creaking_snd = None
dam_snd = None
waterfall_snd = None
waterpipe_snd = None
hz_snd = None

commands = [["error", "s"],
        ["id", "I"],
	["button_pressed", "I"],
	["control_pos", "II"],
	["light_on", "I"],		
	["light_off", "I"],		
	["engage_dc_volt", ""],		
	["disengage_dc_volt", ""],
	["engage_dc_amp", ""],	
	["disengage_dc_amp", ""],	
	["set_vfd", "I"],
        ["set_hz", "I"]]

def getMessengers():
	Aports = glob.glob("/dev/ttyACM*")
	# Uports = glob.glob("/dev/ttyUSB*") # Handles lower-speed RS-485 ports separately
	msgs = [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=57600),commands) for serial_device in Aports]
	# msgs += [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=2400),commands) for serial_device in Uports]
	return msgs

# Initial state of the power plant (on, in case of power failure while running)

transformer_on = True
generator_on = True
ac_on = True
dc_level = 255 # From 0 (unpowered) to 255 (max capacity)
freq = 55
adj_res = 0 # 0 to 255 "Innstillingsmotstand", currently not connected
shunt = 0 # 0 to 255 "Shunt", currently not connected
water = 255 # 0 to 255 "Water pressure", currently not connected to anything but sound

# creaking_snd = None
# dam_snd = None
# waterfall_snd = None

def stateCommands(msgs):
        global hydro_snd
        global creaking_snd
        global dam_snd
        global waterfall_snd
        global waterpipe_snd
        global hz_snd

        global transformer_on 
        global generator_on 
        global ac_on 
        global dc_level
        global freq
        global adj_res
        global shunt
        global water
        
        if (transformer_on):
                if __debug__:
                        print("transformer on");
                [msg.send("light_on", 0) for msg in msgs]
                [msg.send("light_off", 1) for msg in msgs]
        else:
                if __debug__:
                        print("transformer off");
                [msg.send("light_on", 1) for msg in msgs]
                [msg.send("light_off", 0) for msg in msgs]
                
        if (generator_on):
                if __debug__:
                        print("generator on");
                [msg.send("light_on", 2) for msg in msgs]
                [msg.send("light_off", 3) for msg in msgs]
        else:
                if __debug__:
                        print("generator off");
                [msg.send("light_on", 2) for msg in msgs]
                [msg.send("light_off", 3) for msg in msgs]
        
        if (ac_on):
                [msg.send("engage_dc_volt") for msg in msgs]
                if __debug__:
                        print("ac_on");
        else:
                [msg.send("disengage_dc_volt") for msg in msgs]
                if __debug__:
                        print("ac_off");
                        
        [msg.send("set_vfd", dc_level) for msg in msgs]
        if __debug__:
                print("set_vfd {}".format(dc_level));
        
        [msg.send("set_hz", freq) for msg in msgs]
        if __debug__:
                print("set_hz {}".format(freq));

#        hydro_snd.set_volume(min(dc_level, water)/255)        
#        waterfall_snd.set_volume(255 / water);

        if (water > 50 | water == 0):
                waterpipe_snd.set_volume(0.0)
        else:
                waterpipe_snd.set_volume(0.2)

def handleMessage(msg):
        global hydro_snd
        global creaking_snd
        global dam_snd
        global waterfall_snd
        global waterpipe_snd
        global hz_snd

        global transformer_on 
        global generator_on 
        global ac_on 
        global dc_level
        global freq
        global adj_res
        global shunt
        global water
        
        if __debug__:
               print("handleMessage: {}".format(str(msg)))

        if msg == None:
                return;
        
        if msg[0] == "error":
                print("Error: {}\n".format(msg[1]))
        elif msg[0] == "id":
                True # nop for now
        elif msg[0] == "button_pressed":
                btn = msg[1][0]
                if btn == 0: # venstre ut
                        if (transformer_on):
                                hz_snd.fadeout(1000);
                        transformer_on = False
                elif btn == 1: # venstre inn
                        if (not transformer_on):
                                hz_snd.play(fade_ms=1);
                        transformer_on = True
                elif btn == 2: # høyre ut
                        generator_on = False
                elif btn == 3: # høyre inn
                        generator_on = True
        elif msg[0] == "control_pos":
                ctrl = msg[1][0]
                pos = msg[1][1]
                if ctrl == 0: # Turbinregulator
                        if pos == 0: # synker
                                dc_level = max(dc_level-10, 0)
                        elif pos == 1: # nøytral
                                True # nop
                        elif pos == 2: # stiger
                                dc_level = min(dc_level+10, 255)
                elif ctrl == 1: # Instillingsmotstand
                        adj_res = pos
                elif ctrl == 2:
                        shunt = pos
                elif ctrl == 3:
                        True # demagnetize
                elif ctrl == 4:
                        water = max(0,min(255,water+pos))

def mainLoop():
        global hydro_snd
        global creaking_snd
        global dam_snd
        global waterfall_snd
        global waterpipe_snd
        global hz_snd
        
        msgs = getMessengers()
        
        pygame.mixer.init(frequency=44100, size=-16, channels=6, buffer=4096)
        hydro_snd = pygame.mixer.Sound("sounds/hydroelectric_loop.wav")
        hydro_snd.set_volume(0.0)
        hydro_snd.play(loops=-1)
        
        creaking_snd = pygame.mixer.Sound("sounds/creaking_loop.wav")
        creaking_snd.set_volume(0.0)
        creaking_snd.play(loops=-1)

        dam_snd = pygame.mixer.Sound("sounds/damsounds_loop.wav")
        dam_snd.set_volume(0.0)
        dam_snd.play(loops=-1)

        waterfall_snd = pygame.mixer.Sound("sounds/waterfall_loop.wav")
        waterfall_snd.set_volume(0.0)
        waterfall_snd.play(loops=-1)

        waterpipe_snd = pygame.mixer.Sound("sounds/waterpipe_loop.wav")
        waterpipe_snd.set_volume(0.0)
        waterpipe_snd.play(loops=-1)

        hz_snd = pygame.mixer.Sound("sounds/50hz.wav")
        hz_snd.set_volume(0.5)
        hz_snd.play(loops=-1)

        stateCommands(msgs)

        # TODO  Må legge inn noe her som sender stateCommands med jevne mellomrom (hvert minutt?),
        #       sånn i tilfelle
        
        # TODO  Må legge inn noen her som sjekker på nytt (hvet minutt? femte minutt)
        #       om det er nye arduinoer som er koblet til / koblet fra
        
        while True:
                for c in msgs:
                        if __debug__:
                                print("c: {}".format(str(c)))
                        msg = c.receive()
                        handleMessage(msg)
                stateCommands(msgs)

mainLoop()

