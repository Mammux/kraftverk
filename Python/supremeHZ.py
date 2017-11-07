import pygame
from pygame.locals import *
import zmq
import math
import numpy as np
from time import sleep
from array import array
from pygame.mixer import Sound, get_init, pre_init

SILLY = False
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

duration = 3.0          # in seconds
freqs = [45.0, 46.0, 47.0, 48.0, 49.0, 50.0, 51.0, 52.0, 53.0, 54.0, 55.0]
sounds = []
freq = 50

#this sounds totally different coming out of a laptop versus coming out of headphones

sample_rate = 44100
n_samples = int(round(duration*sample_rate))

#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above

for frequency in freqs:

  n = Note(frequency, 0.0)

  print("generating %f", frequency)  

  #play once, then loop forever
  n.play(loops = -1)
  if(frequency == 50.0):
    n.set_volume(1.0)
  else:
    n.set_volume(0.0)

  sounds.append(n)

print(sounds)

sleep(5)

if (not SILLY):
  port = 5556
  context = zmq.Context()
  socket = context.socket(zmq.REQ)
  socket.connect ("tcp://localhost:%s" % port)

  print ("Connecting to server with port %s" % port)

while True:
  if (not SILLY):
    socket.send_string("get_hz_raw")
    freq = int(socket.recv())
  print(freq)

# Decay
  for s in sounds:
    print("Snd: %s Vol: %f" % (s, s.get_volume()))
    s.set_volume(0.0)

  if (freq >= 45 and freq <= 55):
    print ("Turning up %d" % (freq-45))
    sounds[freq-45].set_volume(1.0)

  sleep(10)


