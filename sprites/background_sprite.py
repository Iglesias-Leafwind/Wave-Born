import pygame
from pygame.sprite import Sprite


class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, leftX=0, leftY=0, width=800, height=600):
        Sprite.__init__(self)
        picture = pygame.image.load("sources/imgs/background.png")
        picture = pygame.transform.scale(picture, (width, height))
        self.image = picture.convert_alpha()

        self.rect = pygame.Rect(leftX, leftY, width - 3, height - 3)

        self.yes = True

    def move(self, x=True, forward=True):
        forward = 1 if forward else -1
        if x:
            self.rect.x += forward * 10
        else:
            self.rect.y += forward * 10

    def update(self, vector=0):
        if vector == 0:
            return
        x, y = vector
        self.rect = self.rect.move(x, y)