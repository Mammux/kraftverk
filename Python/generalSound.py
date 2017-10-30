import pygame
import time

pygame.mixer.init(frequency=44100, size=-16, channels=5, buffer=4096)
snd1 = pygame.mixer.Sound("D:\\1942\\Kraftverk\\Lyder\\hydroelectric_loop.wav")
snd2 = pygame.mixer.Sound("D:\\1942\\Kraftverk\\Lyder\\creaking_loop.wav")
snd3 = pygame.mixer.Sound("D:\\1942\\Kraftverk\\Lyder\\damsounds_loop.wav")
snd4 = pygame.mixer.Sound("D:\\1942\\Kraftverk\\Lyder\\waterfall_loop.wav")
snd5 = pygame.mixer.Sound("D:\\1942\\Kraftverk\\Lyder\\waterpipe_loop.wav")
snd1.play(loops=-1)
time.sleep(5.0) 
snd2.play()
time.sleep(5.0) 
snd3.play()
time.sleep(5.0) 
snd4.play()
time.sleep(5.0) 
snd5.play()
time.sleep(15.0) 
