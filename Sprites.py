import pygame

class Wave():
    def __init__(self, center, velocity, clockticks, sound_interval):
        #sound_interval = (sound_start,sound_end)
        self.radius = -velocity*clockticks*sound_interval[0] if sound_interval[0] > 0 else 0
        self.x = center[0]
        self.y = center[1]
        self.thicc = int(clockticks*(sound_interval[1]-sound_interval[0]))
        self.velocity = velocity
        self.sound_interval = sound_interval
        
    def update(self):
        self.radius += self.velocity

    def draw(self,mask):
        pygame.draw.circle(mask,(0,0,255),(self.x,self.y),self.radius,self.thicc)

    def checkLimits(self,WIDTH,HEIGHT):
        limits = [(0,0),(WIDTH,0),(0,HEIGHT),(WIDTH,HEIGHT)]
        return all((abs(limit[0]-self.x) + abs(limit[1]-self.y)) < self.radius for limit in limits)