from pygame import *
from pygame.sprite import *
from pygame.mixer import *
from pygame.font import *
import pygame

class TST(Sprite):
    def __init__(self, leftX=0, leftY=0, width=50, height=50):
        Sprite.__init__(self)
        picture = image.load("./xenomorph.png")
        picture = pygame.transform.scale(picture,(width,height))
        self.image = picture.convert_alpha()

        self.rect = Rect(leftX,leftY,width-3,height-3)

        self.yes = True

    def move(self, x=True, forward=True):
        forward = 1 if forward else -1
        if x:
            self.rect.x += forward * 10
        else:
            self.rect.y += forward * 10

    def update(self,vector):
        x, y = vector
        self.rect = self.rect.move(x,y)

    def scare(self):
        if (self.yes):
            self.rect.x = -110
            self.rect.y = -110
            self.rect.size = (1000,1000)
            self.image = transform.scale(self.image, (1000, 1000))
            self.yes = False
pygame.init()
screen = display.set_mode((800,600))
display.set_caption("Hello World")
font = Font(None,32)

clock = pygame.time.Clock()


sprite_object = TST()

wall_object = TST(100,100)

all_sprites = sprite.Group()
all_sprites.add(wall_object)
all_sprites.add(sprite_object)
velocity = 1
lastKey = None

mixer.init()
mixer.stop()
wree_sound = Sound("./wreee.mp3")
music.load("./background.mp3")
music.play(loops=-1)

while 1:
    clock.tick(144)
    velocity = 3

    screen.fill((0,0,0))

    for e in event.get():
        if e.type == QUIT:
            pygame.quit()
            break
        elif e.type == KEYDOWN or e.type == KEYUP:
            lastKey = pygame.key.get_pressed()

    if lastKey:
        key = lastKey
        if key[K_UP] or key[K_w]:
            undo_up = (0,velocity*2)
            sprite_object.update((0,-1*velocity))
            if sprite_object.rect.colliderect(wall_object.rect):
                sprite_object.update(undo_up)
                text_surface = font.render("WREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",True, (0,0,255))
                Surface.blit(screen, text_surface, (wall_object.rect.x,wall_object.rect.y-30))
                wree_sound.play()
        if key[K_DOWN] or key[K_s]:
            undo_down = (0,-1*velocity*2)
            sprite_object.update((0,velocity))
            if sprite_object.rect.colliderect(wall_object.rect):
                sprite_object.update(undo_down)
                text_surface = font.render("WREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", True, (0, 0, 255))
                Surface.blit(screen, text_surface, (wall_object.rect.x, wall_object.rect.y - 30))
                wree_sound.play()
        if key[K_LEFT] or key[K_a]:
            undo_left = (velocity*2,0)
            sprite_object.update((-1*velocity,0))
            if sprite_object.rect.colliderect(wall_object.rect):
                sprite_object.update(undo_left)
                text_surface = font.render("WREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", True, (0, 0, 255))
                Surface.blit(screen, text_surface, (wall_object.rect.x, wall_object.rect.y - 30))
                wree_sound.play()
        if key[K_RIGHT] or key[K_d]:
            undo_right = (-1*velocity*2,0)
            sprite_object.update((velocity, 0))
            if sprite_object.rect.colliderect(wall_object.rect):
                sprite_object.update(undo_right)
                text_surface = font.render("WREEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", True, (0, 0, 255))
                Surface.blit(screen, text_surface, (wall_object.rect.x, wall_object.rect.y - 30))
                wree_sound.play()
        if key[K_e]:
            sprite_object.scare()


    all_sprites.draw(screen)
    display.update()

