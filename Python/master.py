import glob
import random, sys
import PyCmdMessenger
import pygame
import time
import pickle
from time import sleep
import zmq
import multiprocessing
from  multiprocessing import Process
import soundfile as sf
import sounddevice as sd
import numpy as np

FAIL_EARLY = True

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

# volume: 0.0 to 1.0
def hzData(volume, fs, duration, f):
  return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * int(volume * 16384)).astype(np.float32)

def server():
    global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
    global state
    
    port = 5556
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % port)
    print ("Running server on port: ", port)
    while True:
        # Wait for next request from client
        message = socket.recv()
        print ("Received request: %s" % (message))
        tokens = message.split()
        if (tokens[0] == b"get_hz"):
            socket.send_string("Svar fra master, %d Hz på port %s" % (state['freq'], port))
        elif (tokens[0] == b"set_hz" and len(tokens) == 2):
            state['freq'] = int(tokens[1])
            socket.send_string("Svar fra master, har satt %d Hz på port %s" % (state['freq'], port))
        elif (tokens[0] == b"get_vfd"):
            socket.send_string("Svar fra master, %d%% VFD på port %s" % (state['ac_level'], port))
        elif (tokens[0] == b"set_vfd" and len(tokens) == 2):
            state['ac_level'] = int(tokens[1])
            socket.send_string("Svar fra master, har satt %d%% VFD på port %s" % (state['ac_level'], port))
        elif (tokens[0] == b"get_water"):
            socket.send_string("Svar fra master, %d water på port %s" % (state['water'], port))
        elif (tokens[0] == b"set_water" and len(tokens) == 2):
            state['water'] = int(tokens[1])
            socket.send_string("Svar fra master, har satt %d water på port %s" % (state['water'], port))
        elif (tokens[0] == b"creaking" and len(tokens) == 2):
            creak_level = float(tokens[1])
            socket.send_string("Svar fra master, har satt creaking vol %f på port %s" % (creak_level, port))
            state['creaking'] = creak_level
        elif (tokens[0] == b"damming" and len(tokens) == 2):
            dam_level = float(tokens[1])
            socket.send_string("Svar fra master, har satt damming vol %f på port %s" % (dam_level, port))
            state['damming'] = dam_level
        else:
            socket.send_string("Error: %s" % str(tokens))

def getMessengers():
    Aports = glob.glob("/dev/serial/by-id/usb-1a86*")
    Uports = glob.glob("/dev/serial/by-id/usb-FTDI*") # Handles lower-speed RS-485 ports separately
    msgs = [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=57600),commands) for serial_device in Aports]
    msgs += [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=2400),commands) for serial_device in Uports]
    return msgs

# Initial state of the power plant 

state = multiprocessing.Manager().dict()

defState = {
    'transformer_on' : True,
    'generator_on' : True,
    'dc_on' : True,
    'ac_level' : 150, # From 0 (unpowered) to 255 (max capacity)
    'freq' : 50,
    'adj_res' : 0, # 0 to 255 "Innstillingsmotstand", currently not connected
    'shunt' : 0, # 0 to 255 "Shunt", currently not connected
    'water' : 150, # 0 to 255 "Water pressure", currently not connected to anything but sound
    'creaking' : 0.0,
    'damming' : 0.0
    }

fileState = {'bogus':0}

try:
    fileState = pickle.load( open("state.p", "rb"))
    print("Loaded stored values")
except FileNotFoundError:
    print("File not found, using default state values")

for key in defState:
    try:
        state[key] = fileState[key]
    except:
        state[key] = defState[key]

def stateCommands(msgs):
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
        global state
        
        if (state['transformer_on']):
                if __debug__:
                        print("transformer on");
                [msg.send("light_on", 0) for msg in msgs]
                [msg.send("light_off", 3) for msg in msgs]
        else:
                if __debug__:
                        print("transformer off");
                [msg.send("light_on", 3) for msg in msgs]
                [msg.send("light_off", 0) for msg in msgs] 
                
        if (state['generator_on']):
                if __debug__:
                        print("generator on");
                [msg.send("light_on", 2) for msg in msgs] 
                [msg.send("light_off", 1) for msg in msgs]
                [msg.send("set_vfd", state['ac_level']) for msg in msgs]
                if __debug__:
                    print("set_vfd {}".format(state['ac_level']));
        else:
                if __debug__:
                        print("generator off");
                [msg.send("light_on", 1) for msg in msgs]
                [msg.send("light_off", 2) for msg in msgs] 
                [msg.send("set_vfd", 0) for msg in msgs]
                if __debug__:
                    print("set_vfd {}".format(0));
    
        
        if (state['dc_on']):
                [msg.send("engage_dc_volt") for msg in msgs]
                if __debug__:
                        print("dc_on");
        else:
                [msg.send("disengage_dc_volt") for msg in msgs]
                if __debug__:
                        print("dc_off");
                        
        [msg.send("set_hz", state['freq']) for msg in msgs]
        if __debug__:
                print("set_hz {}".format(state['freq']));

        if __debug__:
                print("water {}".format(state['water']));

        waterfall_snd.set_volume((state['water']/255)*0.25);

        if (state['water'] > 50 or state['water'] == 0):
                hydro_snd.set_volume(state['water']/255)        
                waterpipe_snd.set_volume(0.0)
        else:
                hydro_snd.set_volume((state['water']/255) * 0.25)        
                waterpipe_snd.set_volume(0.5)

        creaking_snd.set_volume(state['creaking'])
    
        fs = 44100
        length = 1
        stuff = hzData(min(state['ac_level'],state['water']) / 255, fs, length, state['freq'])
        sd.play(stuff,loop=True,device=0)

def handleMessage(msg):
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
        global state
        
        if msg == None:
                return;

        if True or __debug__:
               print("Message: {}".format(str(msg)))
        
        if msg[0] == "error":
                print("Error: {}\n".format(msg[1]))
        elif msg[0] == "id":
                True # nop for now
        elif msg[0] == "button_pressed":
                btn = msg[1][0]
                if btn == 0: # venstre ut
                        if (state['transformer_on']):
                                hz_snd.fadeout(1000);
                        state['transformer_on'] = False
                elif btn == 1: # venstre inn
                        if (not state['transformer_on']):
                                hz_snd.play(fade_ms=1000);
                        state['transformer_on'] = True
                elif btn == 2: # høyre ut
                        state['generator_on'] = False
                elif btn == 3: # høyre inn
                        state['generator_on'] = True
        elif msg[0] == "control_pos":
                ctrl = msg[1][0]
                pos = msg[1][1]
                if ctrl == 0: # Turbinregulator
                        if pos == 0: # synker
                                state['ac_level'] = max(state['ac_level']-10, 0)
                        elif pos == 1: # nøytral
                                True # nop
                        elif pos == 2: # stiger
                                state['ac_level'] = min(state['ac_level']+10, 255)
                elif ctrl == 1: # Instillingsmotstand
                        state['adj_res'] = pos
                elif ctrl == 2:
                        state['shunt'] = pos
                elif ctrl == 3:
                        True # demagnetize
                elif ctrl == 4:
                        state['water'] = max(0,min(255,state['water']+(pos*5)))
                elif ctrl == 5:
                        state['water'] = max(0,min(255,state['water']-(pos*5)))

def mainLoop():
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd

        Process(target=server).start()
        
        msgs = getMessengers()
        
        pygame.mixer.init(frequency=44100, size=-16, channels=6, buffer=4096)
        hz_snd = pygame.mixer.Sound("sounds/50hz.wav")
        hz_snd.set_volume(0.0)
        hz_snd.play(loops=-1)

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

        stateCommands(msgs)

        # TODO  Burde legge inn noe her som sender stateCommands med jevne mellomrom (hvert minutt?),
        #       sånn i tilfelle
        
        # TODO  Må legge inn noen her som sjekker på nytt (hvet minutt? femte minutt)
        #       om det er nye arduinoer som er koblet til / koblet fra
        
        prevStateTime = time.time()
        prevMsgsTime = time.time()

        while True:
                for c in msgs:
                        if __debug__:
                                if (c == None): print("%s: no c" % (c))
                                if (c.board == None): print("%s: !c.board" % (c))
                                if (c.board.connected == False): print("%s: !c.board.connected" % (c))
                                if (c.board.comm == None): print("%s: !c.board.comm" % (c))
                                if (c.board.comm.is_open == False): print("%s: !c.board.comm.is_open" % (c))
                        try:
                                if (c.board.comm.in_waiting > 0):
                                        msg = c.receive()
                                        handleMessage(msg)
                        except KeyboardInterrupt:
                                raise
                        except EOFError:
                                if (FAIL_EARLY): raise
                                print("RECOVERABLE ERROR: EOFError")
                                sleep(5)
                                msgs = getMessengers()
                                break
                        except OSError:
                                if (FAIL_EARLY): raise
                                print("RECOVERABLE ERROR: OSError")
                                sleep(5)
                                msgs = getMessengers()
                                break
                        except:
                                print("Unexpected error:", sys.exc_info()[0])
                                

                if (time.time() - prevStateTime > 5):
                        stateCommands(msgs)
                        prevStateTime = time.time()

                if (time.time() - prevMsgsTime > 120):
                        pickle.dump(state, open("state.p", "wb"))
                        if (not FAIL_EARLY): msgs = getMessengers()
                        prevMsgsTime = time.time()
#endif                        

mainLoop()

