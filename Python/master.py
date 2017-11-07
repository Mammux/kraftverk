import glob
import random, sys
import PyCmdMessenger
import pygame
import time
import pickle
from time import sleep
import zmq
import multiprocessing
import os
from  multiprocessing import Process, Manager
import numpy as np
import os.path

FAIL_EARLY = False

# Sound channels
hydro_snd = None
creaking_snd = None
dam_snd = None
waterfall_snd = None
waterpipe_snd = None
hz_snd = None

# For hz sound making
prevHz = 50
prevStrength = 255

# Cmd Messenger commands - has to be the same everywhere
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

# Volume: 0.0 to 1.0
def hzData(volume, fs, duration, f):
  return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * int(volume * 16384)).astype(np.float32)

# Separate process for responding to requests
def server(state):
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
        elif (tokens[0] == b"get_hz_raw"):
            socket.send_string("%d" % (state['freq']))
        elif (tokens[0] == b"set_hz_bump" and len(tokens) == 2):
            state['freq_bump'] = int(tokens[1])
            socket.send_string("Svar fra master, har satt %d Hz bump på port %s" % (state['freq_bump'], port))
        elif (tokens[0] == b"get_hz_bump" and len(tokens) == 2):
            state['freq_bump'] = int(tokens[1])
            socket.send_string("Svar fra master, har %d Hz bump på port %s" % (state['freq_bump'], port))
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
        elif (tokens[0] == b"set_creaking" and len(tokens) == 2):
            creak_level = float(tokens[1])
            socket.send_string("Svar fra master, har satt creaking vol %f på port %s" % (creak_level, port))
            state['creaking'] = creak_level
        elif (tokens[0] == b"set_damming" and len(tokens) == 2):
            dam_level = float(tokens[1])
            socket.send_string("Svar fra master, har satt damming vol %f på port %s" % (dam_level, port))
            state['damming'] = dam_level
        elif (tokens[0] == b"get_creaking"):
            socket.send_string("Svar fra master, har creaking vol %f" % (state['creaking']))
        elif (tokens[0] == b"get_damming"):
            socket.send_string("Svar fra master, har damming vol %f" % (state['damming']))
        elif (tokens[0] == b"get_state"):
            socket.send_string("Svar fra master: %s" % (str(state)))
        elif (tokens[0] == b"help"):
            socket.send_string("get_hz, set_hz N, get_vfd, set_vfd N, get_water, set_water N, creaking n.n, damming n.n");
        else:
            socket.send_string("Error (try 'help'): %s" % str(tokens))

# Establish connections with the devices
def getMessengers():
    Aports = glob.glob("/dev/serial/by-id/usb-1a86*")
    Uports = glob.glob("/dev/serial/by-id/usb-FTDI*") # Handles lower-speed RS-485 ports separately
    msgs = [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=14400),commands) for serial_device in Aports]
    msgs += [PyCmdMessenger.CmdMessenger(PyCmdMessenger.ArduinoBoard(serial_device,baud_rate=2400),commands) for serial_device in Uports]
    return msgs

# Setting initial state of the power plant 
def setupState(st):
    defState = {
        'transformer_on' : True,
        'generator_on' : True,
        'dc_on' : True,
        'ac_level' : 255, # From 0 (unpowered) to 255 (max capacity)
        'freq' : 50,
        'freq_bump': 0,
        'adj_res' : 0, # 0 to 255 "Innstillingsmotstand", currently not connected
        'shunt' : 0, # 0 to 255 "Shunt", currently not connected
        'water' : 255, # 0 to 255 "Water pressure", currently not connected to anything but sound
        'creaking' : 0.0,
        'damming' : 0.0
        }
    fileState = {'bogus':0}

    try:
        f = open("state.p", "rb")
        fileState = pickle.load(f)
        print("Loaded stored values")
    except FileNotFoundError:
        print("File not found, using default state values")
    for key in defState:
        try:
            st[key] = fileState[key]
        except:
            st[key] = defState[key]

# Separated update methods
def updateVFDLights(msgs, state):
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
        
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

def updateWater(msgs, state):
        if __debug__:
                print("water {}".format(state['water']));

        waterfall_snd.set_volume((state['water']/255)*0.25);

        if (state['water'] > 50 or state['water'] == 0):
                hydro_snd.set_volume(state['water']/255)        
                waterpipe_snd.set_volume(0.0)
        else:
                hydro_snd.set_volume((state['water']/255) * 0.25)        
                waterpipe_snd.set_volume(0.5)

def updateFreq(msgs, state):
        [msg.send("set_hz", state['freq']) for msg in msgs]
        if __debug__:
                print("set_hz {}".format(state['freq']));

def updateDC(msgs, state):
        if (state['dc_on']):
                [msg.send("engage_dc_volt") for msg in msgs]
                if __debug__:
                        print("dc_on")
        else:
                [msg.send("disengage_dc_volt") for msg in msgs]
                if __debug__:
                        print("dc_off")

# Updating devices about current state
def stateCommands(msgs, state):
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
        global prevHz, prevStrength

        updateVFDLights(msgs, state)        
        
        updateFreq (msgs, state)

        updateDC (msgs, state)

        updateWater(msgs, state)

        creaking_snd.set_volume(state['creaking'])

# Take care of a received message from one of the Arduino devices
def handleMessage(msg, msgs, state):
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd
        
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
                updateVFDLights(msgs, state)
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
                        updateVFDLights(msgs, state)
                elif ctrl == 1: # Instillingsmotstand
                        state['adj_res'] = pos
                        state['freq'] = int(45 + (10 * (state['adj_res']/255)) + state['freq_bump'])
                        updateFrq(msgs, state)
                elif ctrl == 2:
                        ch = abs(state['shunt'] - pos)
                        state['shunt'] = pos
                        # Shunting reduces noise
                        state['creaking'] = max(0.0, state['creaking'] - ch/255)
                        state['damming'] = max(0.0, state['damming'] - ch/255)
                elif ctrl == 3:
                        True # demagnetize
                elif ctrl == 4:
                        state['water'] = max(0,min(255,state['water']+(pos*5)))
                        updateWater(msgs, state)
                elif ctrl == 5:
                        state['water'] = max(0,min(255,state['water']-(pos*5)))
                        updateWater(msgs, state)

def initSound():
        global hydro_snd, creaking_snd, dam_snd, waterfall_snd, waterpipe_snd, hz_snd

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

# Do some setup, then loop receiving messages and handling changes
def mainLoop():
        initSound();

        manager = Manager();
        state = manager.dict();
        setupState(state);
        Process(target=server,args=(state,)).start();
        
        msgs = getMessengers()

        stateCommands(msgs, state)

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
                                        handleMessage(msg, msgs, state)
                        except KeyboardInterrupt:
                                print("Terminating master.py")
                                sys.exit()
                        except EOFError as err:
                                if (FAIL_EARLY): raise
                                print("RECOVERABLE ERROR: EOFError: %s" % c.board.device)
                                print("Error: %s" % err)
                                sleep(5)
                                msgs = getMessengers()
                                break
                        except OSError as err:
                                if (FAIL_EARLY): raise
                                print("RECOVERABLE ERROR: OSError: %s" % c.board.device)
                                print("Error: %s" % err)
                                sleep(5)
                                msgs = getMessengers()
                                break
                        except:
                                print("Unexpected error:", sys.exc_info()[0])
                                

                if (time.time() - prevStateTime > 5):
                        stateCommands(msgs, state)
                        prevStateTime = time.time()

                if (time.time() - prevMsgsTime > 120):
                        print("Dumping state and recreating messengers")
                        tmpState = {}
                        statKeys = [ 'transformer_on', 'generator_on', 'dc_on',
                                 'ac_level', 'freq', 'freq_bump', 'adj_res', 'shunt',
                                 'water', 'creaking', 'damming' ]
                        for k in statKeys:
                          tmpState[k] = state[k]
                        pickle.dump(tmpState, open("state.p", "wb"))
                        if (not FAIL_EARLY): msgs = getMessengers()
                        prevMsgsTime = time.time()

if __name__ == '__main__':
    mainLoop();
    

