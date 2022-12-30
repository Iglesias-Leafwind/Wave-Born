import pygame
from pygame import *
from pygame.mixer import *
import random
from models.monsters import Monster, BirdLike, Spawner, SpiderLike, TurtleLike, Whale
from models.player import Player
from models.wave import Waves
from models.world import World
from menu.mainmenu import MainMenu
from sprites.background_sprite import BackgroundSprite
from sprites.monster_sprites import SpiderLikeSprite, BirdLikeSprite, TurtleLikeSprite, WhaleSprite
from sprites.player_sprite import PlayerSprite
from models.sound import Sound as sd

if __name__ == "__main__":
    WIDTH = 1024
    HEIGHT = 640
    SCALE = 32
    blocks_x = int(WIDTH / SCALE)
    blocks_y = int(HEIGHT / SCALE)

    mixer.init()
    music.set_volume(0.5)
    music.load("sources/sounds/breeze_bay.mp3")
    music.play(loops=-1)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    menu = MainMenu()
    menu.set_show()
    world = World(blocks_x,blocks_y,SCALE)    
    pygame.font.init()
    while menu is None or not menu.exit:
        
        # init screen
        screen.fill((0, 0, 255))

        all_sprites = sprite.Group()

        world.generateWorld(menu.difficulty, 2)
        world.startWorld()

        # loading the images
        sprite_object = BackgroundSprite(width=WIDTH, height=HEIGHT)
        player = Player(50, 500)
        Monster.set_user_pos(player.pos)
        player.controls(pygame.K_a, pygame.K_d, pygame.K_SPACE)
        player_sprite = PlayerSprite(HEIGHT, player, [SpiderLikeSprite, BirdLikeSprite, TurtleLikeSprite], SCALE)
        Player.SPRITE = player_sprite

        #spawner and templates
        spawner = Spawner()
        bird = BirdLike(width=WIDTH, height=HEIGHT, stop_width=WIDTH, stop_height=HEIGHT // 2)
        spider = SpiderLike(width=WIDTH, height=HEIGHT, start_width=100, stop_width=WIDTH, stop_height=460,
                            attack_prob=0.05)
        turtle = TurtleLike(width=WIDTH, height=HEIGHT, start_width=100, stop_width=WIDTH, stop_height=460,
                            attack_prob=0.01)
        whale = Whale(width=WIDTH, height=HEIGHT, stop_width=WIDTH, stop_height=HEIGHT, attack_prob=1)
        
        #initialize sprite objects
        bird_sprite = BirdLikeSprite([], WIDTH, HEIGHT, SCALE)

        spider_sprite = SpiderLikeSprite([], WIDTH, HEIGHT, SCALE)
        SpiderLike.SPRITE = spider_sprite

        turtle_sprite = TurtleLikeSprite([], WIDTH, HEIGHT, SCALE)
        TurtleLike.SPRITE = turtle_sprite

        whale_sprite = WhaleSprite([], SCALE)
        Whale.SPRITE = whale_sprite

        all_sprites.add(sprite_object)
        all_sprites.add(player_sprite)

        clock = pygame.time.Clock()

        mask = pygame.Surface((WIDTH, HEIGHT))
        mask.set_colorkey((0, 0, 255))
        # mask.fill(0)

        lastKey = None
        waves = Waves()

        opened_menu = False
        hardmode = False
        moved = 0
        for chunk in world.loaded_chunks:
            if chunk:
                all_sprites.add(chunk)

        while 1:
            #initial arguments
            camera_move = True
            movement = 0
            clock.tick(144)
            
            #process input
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
                #update game
                
                if(random.randint(0,100) < 5 and world.num_monsters > (len(bird_sprite.monsters) + len(spider_sprite.monsters) + len(turtle_sprite.monsters))):
                    selectMonster = random.randint(0,100)
                    if(selectMonster <= 19 and len(whale_sprite.monsters) < 1):
                        whale_sprite._add_monster(spawner.spawn_monster(whale))
                    elif(selectMonster <= 44):
                        bird_sprite._add_monster(spawner.spawn_monster(bird))
                    elif(selectMonster <= 69):
                        spider_sprite._add_monster(spawner.spawn_monster(spider))
                    elif(selectMonster <= 100):
                        turtle_sprite._add_monster(spawner.spawn_monster(turtle))
                
                # world interaction
                moved += movement
                if int(moved / (SCALE * 16)) == 1:
                    removed, added = world.loadNextChunk()
                    if removed:
                        all_sprites.remove(removed)
                    if added:
                        all_sprites.add(added)
                        try:
                            all_sprites.add(added.chunk.end_sprite)        
                        except:
                            pass
                    moved = 0
                elif (int(moved / (SCALE * 16)) == -1):
                    removed, added = world.loadPrevChunk()
                    if removed:
                        all_sprites.remove(removed)
                    if added:
                        all_sprites.add(added)
                        try:
                            all_sprites.remove(added.chunk.end_sprite)
                        except:
                            pass
                    
                    moved = 0
                if (camera_move):
                    # world movement
                    world.moveWorld(movement)
                    world.moveCamera(movement)
                    
                    for wave in waves:
                        wave.x -= movement
                    # counter entity movement with world
                    player_sprite.update_camera_movement(movement)
                    bird_sprite.update_camera_movement(movement)
                    spider_sprite.update_camera_movement(movement)
                    turtle_sprite.update_camera_movement(movement)
                    whale_sprite.update_camera_movement(movement)

                for wave in waves:
                    if (wave.checkLimits(WIDTH, HEIGHT)):
                        waves.remove(wave)
                    else:
                        wave.update()
                    
                if player.won:
                    #instead of game over -> game win
                    menu.game_over(True)
                    sd.stop_all_sounds()
                    menu.mainloop(screen)
                    break
                
                if player.dead or world.timeout():
                    menu.game_over(False)
                    sd.stop_all_sounds()
                    menu.mainloop(screen)
                    break
                
                #render
                # create cover surface
                mask.fill(0)

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
                
            pygame.display.flip()
