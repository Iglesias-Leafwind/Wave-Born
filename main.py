import pygame
from pygame import *
from pygame.sprite import *
from pygame.mixer import *
import random

from models.game_objects import Player, BirdLike, Spawner, SpiderLike
from menu.menu import Menu
from sprites.sprites import PlayerSprite, BirdLikeSprite, SpiderLikeSprite
from wave import Wave


class TST(Sprite):
    def __init__(self, leftX=0, leftY=0, width=800, height=600):
        Sprite.__init__(self)
        picture = image.load("sources/imgs/background.png")
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

    def update(self, vector=0):
        if vector == 0:
            return
        x, y = vector
        self.rect = self.rect.move(x, y)


if __name__ == "__main__":
    WIDTH = 800
    HEIGHT = 600
    SCALE = 32
    mixer.init()
    music.set_volume(0.5)
    # music.load("sources/sounds/breeze_bay.mp3")
    # music.play(loops=-1)

    # init pygame
    pygame.init()

    # init screen
    screen = pygame.display.set_mode((800, 600))
    screen.fill((0, 0, 255))

    # loading the images
    sprite_object = TST(width=WIDTH, height=HEIGHT)
    player = Player()
    player.controls(pygame.K_a, pygame.K_d, pygame.K_SPACE)
    player_sprite = PlayerSprite(player, SCALE)

    bird = BirdLike(stop_width=WIDTH, stop_height=HEIGHT)
    spawner = Spawner()
    birds = [spawner.spawn_monster(bird) for _ in range(10)]
    bird_sprite = BirdLikeSprite(birds, SCALE)

    spider = SpiderLike(stop_width=WIDTH, stop_height=HEIGHT)
    spiders = [spawner.spawn_monster(spider) for _ in range(10)]
    spider_sprite = SpiderLikeSprite(spiders, SCALE)

    all_sprites = sprite.Group()
    all_sprites.add(sprite_object)
    all_sprites.add(player_sprite)
    all_sprites.add(bird_sprite)
    all_sprites.add(spider_sprite)

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
    opened_menu = False
    hardmode = False

    while 1:
        clock.tick(144)
        for e in event.get():
            if e.type == QUIT:
                pygame.quit()
                break

            elif e.type == KEYDOWN or e.type == KEYUP:
                if e.key == K_ESCAPE and not opened_menu:
                    menu.set_show()
                    opened_menu = True
                else:
                    opened_menu = False

                lastKey = pygame.key.get_pressed()
                player.command(e.key)

        if menu.exit:
            pygame.quit()
            break

        if lastKey:
            if lastKey[K_a]:
                player.command(K_a)
                player_sprite.update()
            if lastKey[K_d]:
                player.command(K_d)
                player_sprite.update()

            if lastKey[K_SPACE]:
                player.command(K_SPACE)
                player_sprite.update()
            else:
                player_sprite.can_jump_again()

        if menu and menu.show:
            menu.mainloop(screen)
        else:
            # create cover surface
            mask.fill(0)
            if (random.randint(1, 144) == 1):
                waves.append(Wave(
                    [random.randint(0, 800), random.randint(0, 600)],
                    (random.randint(1, 100) / 100),
                    144,
                    [random.randint(0, 25) / 100, random.randint(25, 30) / 100]))

            for wave in waves:
                wave.draw(mask)
            if (not hardmode):
                player_sprite.draw(mask)


            all_sprites.update()
            all_sprites.draw(screen)
            bird_sprite.draw(mask)
            spider_sprite.draw(mask)

            # draw transparent circle and update display
            screen.blit(mask, (0, 0))
            for wave in waves:
                if (wave.checkLimits(800, 600)):
                    waves.remove(wave)

            for wave in waves:
                wave.update()
                # print(
                #    f"------------------------------------------\nR: {wave.radius}\nT: {wave.thicc}\nV: {wave.velocity}\nS: {wave.sound_interval}\n---------------------------")

        pygame.display.flip()
