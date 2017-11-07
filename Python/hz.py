import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib.pylab as plt
from time import sleep
import zmq
import time
import sys

# FREQUENCY DATA

def hzData(volume, fs, duration, f):
  return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * volume).astype(np.float32)

freq = 50
fs = 44100
length = 1

while True:
  port = 5556
  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect ("tcp://localhost:%s" % port)

  print ("Connecting to server with port %s" % port)

  socket.send_string("get_hz_raw")
  freq = int(socket.recv())

  print ("Updated frequency: %d" % freq)

  stuff = hzData(16384, fs, length, freq)
  
  sd.play(stuff,loop=True,mapping=[1],device=4)
  sleep(1)
  
