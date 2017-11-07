import pygame
from pygame.locals import *
import zmq
import math
import numpy as np
from time import sleep
from array import array
from pygame.mixer import Sound, get_init, pre_init
import random

SILLY = True
bits = 16
#the number of channels specified here is NOT 
#the channels talked about here http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.get_num_channels

class Note(Sound):

    def __init__(self, frequency, volume=.1):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

pygame.mixer.init(frequency=44100, size=-bits, channels=1)
pygame.init()

playingOrig = True

duration = 3.0          # in seconds
# freqs = [45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0]
freq = 52.5

#this sounds totally different coming out of a laptop versus coming out of headphones

sample_rate = 44100
n_samples = int(round(duration*sample_rate))

#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above

n = Note(freq, 1.0)
n.play(loops = -1)

if (not SILLY):
  port = 5556
  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect ("tcp://localhost:%s" % port)
  print ("Connecting to server with port %s" % port)

while True:
  if (not SILLY):
    socket.send_string("get_hz_raw")
    freqNew = float(socket.recv())
  if SILLY: freqNew = freq + random.random() - 0.5
  print("f: %f" % freqNew)
  if (freqNew != freq):
    if (playingOrig):
      n2 = Note(freqNew, 1.0)
      n2.play(loops = -1, fade_ms=1000)
      n.fadeout(1000);
    else:
      n = Note(freqNew, 1.0)
      n.play(loops = -1, fade_ms=1000)
      n2.fadeout(1000);
    freqNew = freq;
    playingOrig = not playingOrig
  print("dibadoo")
  sleep(3)


