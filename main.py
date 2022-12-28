import pygame
from pygame import *
from pygame.mixer import *

from models.monsters import Monster, BirdLike, Spawner, SpiderLike, TurtleLike, Whale
from models.player import Player
from models.wave import Waves
from models.world import World
from menu.menu import Menu
from sprites.background_sprite import BackgroundSprite
from sprites.chunk_sprites import BlockSprite
from sprites.monster_sprites import SpiderLikeSprite, BirdLikeSprite, TurtleLikeSprite, WhaleSprite
from sprites.player_sprite import PlayerSprite

if __name__ == "__main__":
    WIDTH = 1024
    HEIGHT = 640
    SCALE = 32
    blocks_x = int(WIDTH / SCALE)
    blocks_y = int(HEIGHT / SCALE)

    # music.load("sources/sounds/breeze_bay.mp3")
    # music.play(loops=-1)

    # init pygame
    menu = None
    pygame.font.init()
    while menu is None or not menu.exit:
        mixer.init()
        music.set_volume(0.5)

        pygame.init()
        # init screen
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill((0, 0, 255))

        all_sprites = sprite.Group()

        world = World("easy", 1)
        world.startWorld()

        # loading the images
        sprite_object = BackgroundSprite(width=WIDTH, height=HEIGHT)
        player = Player(50, 500)
        Monster.set_user_pos(player.pos)
        player.controls(pygame.K_a, pygame.K_d, pygame.K_SPACE)
        player_sprite = PlayerSprite(player, [SpiderLikeSprite, BirdLikeSprite, TurtleLikeSprite], SCALE)
        Player.SPRITE = player_sprite

        bird = BirdLike(width=WIDTH, height=HEIGHT, stop_width=WIDTH, stop_height=HEIGHT // 2)
        spawner = Spawner()
        birds = [spawner.spawn_monster(bird) for _ in range(5)]
        bird_sprite = BirdLikeSprite(birds, WIDTH, HEIGHT, SCALE)

        spider = SpiderLike(width=WIDTH, height=HEIGHT, start_width=100, stop_width=WIDTH, stop_height=470,
                            attack_prob=0.05)
        spiders = [spawner.spawn_monster(spider) for _ in range(1)]
        spider_sprite = SpiderLikeSprite(spiders, WIDTH, HEIGHT, SCALE)
        SpiderLike.SPRITE = spider_sprite

        turtle = TurtleLike(width=WIDTH, height=HEIGHT, start_width=100, stop_width=WIDTH, stop_height=470,
                            attack_prob=0.01)
        turtles = [spawner.spawn_monster(turtle) for _ in range(3)]
        turtle_sprite = TurtleLikeSprite(turtles, WIDTH, HEIGHT, SCALE)
        TurtleLike.SPRITE = turtle_sprite

        whale = Whale(width=WIDTH, height=HEIGHT, stop_width=WIDTH, stop_height=HEIGHT, attack_prob=0.1)
        whale_sprite = WhaleSprite([whale], SCALE)
        Whale.SPRITE = whale_sprite

        all_sprites.add(sprite_object)
        all_sprites.add(player_sprite)

        clock = pygame.time.Clock()

        mask = pygame.Surface((WIDTH, HEIGHT))
        mask.set_colorkey((0, 0, 255))
        # mask.fill(0)

        lastKey = None
        waves = Waves()

        menu = Menu()
        opened_menu = False
        hardmode = False
        moved = 0
        chunk_sprites = {}
        for idx,chunk in enumerate(world.loaded_chunks):
            if chunk:
                chunk_sprites[idx-2] = BlockSprite(chunk, blocks_x, blocks_y, SCALE)
                all_sprites.add(chunk_sprites[idx-2])

        while 1:
            camera_move = True
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
                    # player.command(e.key)

            if menu.exit:
                pygame.quit()
                break

            player.controls(menu.left_key, menu.right_key, menu.jump_key)

            if lastKey:
                if lastKey[player.left_key]:
                    player.command(player.left_key)
                    if (world.current_chunk <= 0 or world.current_chunk >= len(world.world_chunks) - 1):
                        camera_move = False
                    movement = -1
                if lastKey[player.right_key]:
                    player.command(player.right_key)
                    if (world.current_chunk >= len(world.world_chunks) - 1 or world.current_chunk <= 0):
                        camera_move = False
                    movement = 1
                if lastKey[player.jump_key]:
                    if (not player_sprite.jumping and not player_sprite.falling):
                        player.command(player.jump_key)
                        movement = -player.direction[0]
                else:
                    player_sprite.can_jump_again()

            if menu and menu.show:
                menu.mainloop(screen)
            else:
                # create cover surface
                #mask.fill(0)

                # world interaction
                moved += movement
                if int(moved / (SCALE * 16)) >= 1:
                    _, added = world.loadNextChunk()
                    if added:
                        if world.current_chunk+2 not in chunk_sprites:
                            chunk_sprites[world.current_chunk+2] = BlockSprite(added, blocks_x, blocks_y, SCALE)
                        all_sprites.add(chunk_sprites[world.current_chunk+2])
                        try:
                            all_sprites.remove(chunk_sprites[world.current_chunk-2])
                            all_sprites.add(added.end_sprite)
                        except:
                            pass
                    moved = 0
                elif (int(moved / (SCALE * 16)) <= -1):
                    _, added = world.loadPrevChunk()
                    if added:
                        all_sprites.add(chunk_sprites[world.current_chunk-2])
                        try:
                            all_sprites.remove(chunk_sprites[world.current_chunk+2])
                            all_sprites.remove(added.end_sprite)
                        except:
                            pass
                    moved = 0
                if (camera_move):
                    # world movement
                    world.moveWorld(movement)
                    for i in range(world.current_chunk-2,world.current_chunk+3):
                        try:
                            chunk_sprites[i].move((-movement, 0))
                        except:
                            pass
                    # counter entity movement with world
                    player_sprite.update_camera_movement(movement)
                    bird_sprite.update_camera_movement(movement)
                    spider_sprite.update_camera_movement(movement)
                    turtle_sprite.update_camera_movement(movement)
                    whale_sprite.update_camera_movement(movement)

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
                screen.blit(world.get_time_passed_surface(), (0,0))
                
                for wave in waves:
                    if (wave.checkLimits(WIDTH, HEIGHT)):
                        waves.remove(wave)

                for wave in waves:
                    wave.update()
                
                #if player.dead or world.timeout():
                    #menu.game_over()
                    #menu.mainloop(screen)
                    #sd.stop_all_sounds()
                #    break
            
            pygame.display.flip()
