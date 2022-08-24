import pygame

pygame.mixer.init()
crash_sound = pygame.mixer.Sound("crash.wav")
crash_sound.play()
