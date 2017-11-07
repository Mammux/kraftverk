import soundfile as sf
import sounddevice as sd
import numpy as np
# import matplotlib.pylab as plt
from time import sleep
import zmq
import time
import sys

# FREQUENCY DATA

# def hzData(volume, fs, duration, f):
#   return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * volume).astype(np.float32)


freq = 50.0
fs = 44100
length = 50
actualFreq = 0.0

port = 5556
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

print ("Connecting to server with port %s" % port)

while True:
  socket.send_string("get_hz_raw")
  freq = int(socket.recv())

  snd = hzData(16384, fs, length,actualFreq)
  sd.play(snd,loop=True)


  print ("Updated frequency: %f vs now playing: %f" % (freq, actualFreq))
  if (freq != actualFreq):
    actualFreq = (actualFreq * 9 + freq) / 10
    newstuff = hzData(16384, fs, length,actualFreq)
    snd[:] = newstuff
  
    # sd.play(stuff,loop=True)

  sleep(1)
  
