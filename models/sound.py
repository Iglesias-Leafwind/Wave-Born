from pygame import mixer
from pygame.mixer import *


class Sound(mixer.Sound):
    _all_sounds = set()
    _ID = 0

    def __init__(self, file):
        super(Sound, self).__init__(file)
        self.id = self._next_id()
        Sound._all_sounds.add(self)

    def play(self, **kwargs):
        self.stop()
        self.set_volume(music.get_volume())
        super(Sound, self).play(**kwargs)

    @classmethod
    def stop_all_sounds(cls):
        for s in Sound._all_sounds:
            s.stop()
        Sound._all_sounds.clear()

    @classmethod
    def pop_sound(cls, id):
        Sound._all_sounds.remove(id)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other
        return self.id == other.id

    def _next_id(self):
        id = Sound._ID
        Sound._ID = id + 1
        return id
