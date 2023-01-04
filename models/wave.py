import pygame

#object wave that represents a sound wave in the game
class Wave:
    #creates a wave with a center, velocity,radius,thiccness
    #center [int,int]- wave center in pixels on screen
    #velocity (int) - wave speed in pixels per frame on screen
    #clocktick (int) - how many frames per second are represented
    #sound_interval [int,int]- determines the sound interval of the sound basicly
    # after play when does the sound start and end (anything audible)
    # this sound interval detyermines the thiccness and radius of the sound
    def __init__(self, center, velocity, clockticks, sound_interval):
        # sound_interval = (sound_start,sound_end)
        clockticks = 3 * clockticks / 4
        self.radius = -velocity * clockticks * sound_interval[0] if sound_interval[0] > 0 else 0
        self.x = center[0]
        self.y = center[1]
        self.thicc = int(clockticks * (sound_interval[1] - sound_interval[0]))
        self.velocity = velocity
        self.sound_interval = sound_interval

    #update will just increase the wave radius each frame based on its velocity
    def update(self):
        self.radius += self.velocity
    
    #draw will draw the wave in its currenyt state to the given mask
    #it was used pygame.draw.rect instead of pygame.draw.circle because
    #pygame circle was extremely slow so a rect with curved edges is a fast drawing circle
    def draw(self, mask):
        #pygame.draw.circle(mask, (0, 0, 255), (self.x, self.y), self.radius, self.thicc)
        pygame.draw.rect(mask,(0,0,255), pygame.Rect(self.x-self.radius/2,self.y-self.radius/2,self.radius,self.radius), self.thicc, self.radius)

    #this method checks the circle to see if its outside the screen returning true to it can be deleted
    def checkLimits(self, WIDTH, HEIGHT):
        limits = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
        return all((abs(limit[0] - self.x) + abs(limit[1] - self.y)) < self.radius for limit in limits)

# this class is a singleton where it will store all waves that are present in the game
class Waves:
    _singleton = None

    #initiate singleton
    def __init__(self, waves=None):
        if waves is None:
            waves = []
        self.waves = waves
        self._i = 0
        Waves._singleton = self

    #add wave to singleton
    def add_wave(self, wave):
        self.waves.append(wave)

    #remove wave from singleton
    def remove(self, wave):
        self.waves.remove(wave)

    #initiate or get an existing singleton
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
