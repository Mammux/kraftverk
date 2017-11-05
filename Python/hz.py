import soundfile as sf
import sounddevice as sd
import numpy as np
import matplotlib.pylab as plt

# FREQUENCY DATA

def hzData(volume, fs, duration, f):
  return (np.sin(2*np.pi*np.arange(fs*duration)*f/fs) * volume).astype(np.float32)

fs = 44100
length = 1
stuff = hzData(16384, fs, length, 60)

print(np.max(stuff), np.min(stuff))

sd.play(stuff,loop=False,device='pulse')
sd.wait()


