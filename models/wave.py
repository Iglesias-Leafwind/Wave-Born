import pygame


class Wave:
    def __init__(self, center, velocity, clockticks, sound_interval):
        # sound_interval = (sound_start,sound_end)
        clockticks = 3 * clockticks / 4
        self.radius = -velocity * clockticks * sound_interval[0] if sound_interval[0] > 0 else 0
        self.x = center[0]
        self.y = center[1]
        self.thicc = int(clockticks * (sound_interval[1] - sound_interval[0]))
        self.velocity = velocity
        self.sound_interval = sound_interval

    def update(self):
        self.radius += self.velocity

    def draw(self, mask):
        #pygame.draw.circle(mask, (0, 0, 255), (self.x, self.y), self.radius, self.thicc)
        pygame.draw.rect(mask,(0,0,255), pygame.Rect(self.x-self.radius/2,self.y-self.radius/2,self.radius,self.radius), self.thicc, self.radius)
        
    def checkLimits(self, WIDTH, HEIGHT):
        limits = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
        return all((abs(limit[0] - self.x) + abs(limit[1] - self.y)) < self.radius for limit in limits)


class Waves:
    _singleton = None

    def __init__(self, waves=None):
        if waves is None:
            waves = []
        self.waves = waves
        self._i = 0
        Waves._singleton = self

    def add_wave(self, wave):
        self.waves.append(wave)

    def remove(self, wave):
        self.waves.remove(wave)

    @staticmethod
    def get_or_create(**kwargs):
        if Waves._singleton:
            return Waves._singleton
        return Waves(**kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        if self._i < len(self.waves):
            i = self._i
            self._i += 1
            return self.waves[i]
        self._i = 0
        raise StopIteration()
