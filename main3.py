import pygame, sys
from pygame import *
from pygame.sprite import *
from pygame.mixer import *
from pygame.font import *
import random

from menu.menu import Menu
from wave import Wave


class TST(Sprite):
    def __init__(self, leftX=150, leftY=50, width=500, height=500):
        Sprite.__init__(self)
        picture = image.load("./xenomorph.png")
        picture = pygame.transform.scale(picture, (width, height))
        self.image = picture.convert_alpha()

        self.rect = Rect(leftX, leftY, width - 3, height - 3)

        self.yes = True

    def move(self, x=True, forward=True):
        forward = 1 if forward else -1
        if x:
            self.rect.x += forward * 10
        else:
            self.rect.y += forward * 10

    def update(self, vector):
        x, y = vector
        self.rect = self.rect.move(x, y)


if __name__ == "__main__":
    # init pygame
    pygame.init()

    # init screen
    screen = pygame.display.set_mode((800, 600))
    screen.fill((0, 0, 255))

    # loading the images
    sprite_object = TST()

    all_sprites = sprite.Group()
    all_sprites.add(sprite_object)

    clock = pygame.time.Clock()

    sound_center = (400, 300)

    mask = pygame.Surface((800, 600))
    mask.set_colorkey((0, 0, 255))
    mask.fill(0)

    lastKey = None
    radius = 0
    radius2 = 0
    radius3 = 0
    waves = []
    menu = Menu()
    while 1:
        clock.tick(144)
        for e in event.get():
            if e.type == QUIT:
                pygame.quit()
                break
            elif e.type == KEYDOWN or e.type == KEYUP:
                lastKey = pygame.key.get_pressed()

        if lastKey:
            if lastKey[K_ESCAPE]:
                pygame.quit()
                break
            elif lastKey[K_RETURN]:
                menu.set_show()
            lastKey = None

        if menu and menu.show:
            menu.mainloop(screen)
        else:
            # create cover surface
            mask.fill(0)

            if (random.randint(1, 144) == 1):
                waves.append(Wave(
                    [random.randint(0, 800), random.randint(0, 600)],
                    (random.randint(1, 100) / 10),
                    144,
                    [random.randint(0, 25) / 100, random.randint(25, 30) / 100]))

            for wave in waves:
                wave.draw(mask)

            all_sprites.draw(screen)

            # draw transparent circle and update display
            screen.blit(mask, (0, 0))
            for wave in waves:
                if (wave.checkLimits(800, 600)):
                    waves.remove(wave)

            for wave in waves:
                wave.update()
                print(
                    f"------------------------------------------\nR: {wave.radius}\nT: {wave.thicc}\nV: {wave.velocity}\nS: {wave.sound_interval}\n---------------------------")

        pygame.display.flip()
