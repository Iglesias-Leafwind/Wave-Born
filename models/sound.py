from pygame import mixer
from pygame.mixer import *


class Sound(mixer.Sound):
    def __init__(self, file):
        super(Sound, self).__init__(file)

    def play(self, **kwargs):
        self.stop()
        self.set_volume(music.get_volume())
        super(Sound, self).play(**kwargs)
