import pygame
from pygame.locals import *
import zmq
import math
import numpy

size = (1366, 720)

bits = 16
#the number of channels specified here is NOT 
#the channels talked about here http://www.pygame.org/docs/ref/mixer.html#pygame.mixer.get_num_channels

pygame.mixer.pre_init(44100, -bits, 2)
pygame.init()
# _display_surf = pygame.display.set_mode(size, pygame.HWSURFACE | pygame.DOUBLEBUF)

duration = 1.0          # in seconds
freqs = [45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55]
sounds = []

#this sounds totally different coming out of a laptop versus coming out of headphones

sample_rate = 44100
n_samples = int(round(duration*sample_rate))

#setup our numpy array to handle 16 bit ints, which is what we set our mixer to expect with "bits" up above
buf = numpy.zeros((n_samples, 2), dtype = numpy.int16)
max_sample = 2**(bits - 1) - 1

for frequency in freqs:
  
  for s in range(n_samples):
      t = float(s)/sample_rate    # time in seconds
   
      #grab the x-coordinate of the sine wave at a given time, while constraining the sample to what our mixer is set to with "bits"
      buf[s][0] = int(round(max_sample*math.sin(2*math.pi*frequency*t)))        # left

  sound = pygame.sndarray.make_sound(buf)
  #play once, then loop forever
  sound.play(loops = -1)
  sound.set_volume(0.0)
  sounds.append(sound)

print(sounds)

port = 5556
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect ("tcp://localhost:%s" % port)

print ("Connecting to server with port %s" % port)

while True:
  socket.send_string("get_hz_raw")
  freq = int(socket.recv())
  print(freq)

# Decay
  for s in sounds:
    s.set_volume(max(0.0, s.get_volume()*0.9))

  if (freq >= 45 and freq <= 55):
    sounds[freq-45].set_volume(1.0)

pygame.quit()
