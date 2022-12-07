from pygame import mixer
from pygame.mixer import *


class Sound:
    def __init__(self, file):
        self.sound = mixer.Sound(file)

    def play(self, **kwargs):
        self.sound.set_volume(music.get_volume())
        self.sound.play(**kwargs)
