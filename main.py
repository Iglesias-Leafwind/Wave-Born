import pygame
from pygame import *
from pygame.sprite import *
from pygame.mixer import *
import random

from models.world import *
from models.game_objects import Player, BirdLike, Spawner, SpiderLike, Whale, Wave, TurtleLike
from menu.menu import Menu
from sprites.sprites import PlayerSprite, BirdLikeSprite, SpiderLikeSprite, WhaleSprite, FeatherSprite, TurtleLikeSprite, BlockSprite


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
    WIDTH = 1024
    HEIGHT = 640
    SCALE = 32
    blocks_x = int(WIDTH/SCALE)
    blocks_y = int(HEIGHT/SCALE)

    mixer.init()
    music.set_volume(0.5)
    # music.load("sources/sounds/breeze_bay.mp3")
    # music.play(loops=-1)

    # init pygame
    pygame.init()

    # init screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 255))

    # loading the images
    sprite_object = TST(width=WIDTH, height=HEIGHT)
    player = Player()
    player.controls(pygame.K_a, pygame.K_d, pygame.K_SPACE)
    player_sprite = PlayerSprite(player, [SpiderLikeSprite, BirdLikeSprite, TurtleLikeSprite] ,SCALE)

    bird = BirdLike(stop_width=WIDTH, stop_height=HEIGHT)
    spawner = Spawner()
    birds = [spawner.spawn_monster(bird) for _ in range(5)]
    bird_sprite = BirdLikeSprite(birds, WIDTH, HEIGHT, SCALE)

    spider = SpiderLike(stop_width=WIDTH, stop_height=HEIGHT)
    spiders = [spawner.spawn_monster(spider) for _ in range(5)]
    spider_sprite = SpiderLikeSprite(spiders, WIDTH, HEIGHT, SCALE)

    turtle = TurtleLike(stop_width=WIDTH, stop_height=HEIGHT)
    turtles = [spawner.spawn_monster(turtle) for _ in range(3)]
    turtle_sprite = TurtleLikeSprite(turtles, WIDTH, HEIGHT, SCALE)

    whale = Whale(stop_width=WIDTH, stop_height=HEIGHT)
    whale_sprite = WhaleSprite([whale], SCALE)

    all_sprites = sprite.Group()
    all_sprites.add(sprite_object)
    all_sprites.add(player_sprite)

    clock = pygame.time.Clock()

    mask = pygame.Surface((WIDTH, HEIGHT))
    mask.set_colorkey((0, 0, 255))
    mask.fill(0)

    lastKey = None
    waves = []
    menu = Menu()
    opened_menu = False
    hardmode = False

    world = World("easy", 5)
    world.startWorld()
    moved = 0
    chunk_sprites = []
    for chunk in world.loaded_chunks:
        if chunk:
            chunk_sprites.append(BlockSprite(chunk,blocks_x,blocks_y,SCALE))
            all_sprites.add(chunk_sprites[-1])

    while 1:
        movement = 0
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

        player.controls(menu.left_key, menu.right_key, menu.jump_key)
        
        if lastKey:
            if lastKey[player.left_key]:
                player.command(player.left_key)
                if(world.current_chunk == 0):
                    pass
                    #player moves
                else:
                    movement = -1
                    #player doesn't move
            if lastKey[player.right_key]:
                player.command(player.right_key)
                if(world.current_chunk == len(world.world_chunks)):
                    pass
                #player moves
                else:
                    movement = 1
                    #player doesn't move
            if lastKey[player.jump_key]:
                player.command(player.jump_key)
            else:
                player_sprite.can_jump_again()
            player_sprite.update()

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
            #world interaction
            moved += movement
            if int(moved / (SCALE*16)) >= 1:
                _, added = world.loadNextChunk()
                if added:
                    chunk_sprites.append(BlockSprite(added,blocks_x,blocks_y,SCALE))
                    all_sprites.add(chunk_sprites[-1])
                moved = 0
            elif(int(moved / (SCALE*16)) <= -1):
                _, _ = world.loadPrevChunk()
                moved = 0

                    
            world.moveWorld(movement)
            for sprite in chunk_sprites:
                sprite.move((-movement,0))
    
            all_sprites.update()
            all_sprites.draw(screen)
            bird_sprite.update()
            bird_sprite.draw(screen)
            spider_sprite.update()
            spider_sprite.draw(screen)
            turtle_sprite.update()
            turtle_sprite.draw(screen)
            whale_sprite.update()
            whale_sprite.draw(screen)

            for wave in waves:
                wave.draw(mask)

            if not hardmode:
                player_sprite.draw(mask)
            
            # draw transparent circle and update display
            screen.blit(mask, (0, 0))
            for wave in waves:
                if (wave.checkLimits(WIDTH, HEIGHT)):
                    waves.remove(wave)

            for wave in waves:
                wave.update()
                # print(
                #    f"------------------------------------------\nR: {wave.radius}\nT: {wave.thicc}\nV: {wave.velocity}\nS: {wave.sound_interval}\n---------------------------")

        pygame.display.flip()
