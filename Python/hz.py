import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib.pylab as plt
from time import sleep

# FREQUENCY DATA

def hzData(volume, fs, duration, f):
  return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * volume).astype(np.float32)

fs = 44100
length = 1
stuff = hzData(16384, fs, length, 60)

sd.play(stuff,loop=True,device='pulse')
sleep(5)

stuff = hzData(16384, fs, length, 50)
sd.play(stuff,loop=True,device='pulse')

sleep(5)

stuff = hzData(16384, fs, length, 40)
sd.play(stuff,loop=True,device='pulse')

