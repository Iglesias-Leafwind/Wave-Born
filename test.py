from pygame import *
from sprites.sprites import BlockSprite
from models.world import *

if __name__ == "__main__":
    WIDTH = 1024
    HEIGHT = 640
    SCALE = 32
    blocks_x = int(WIDTH/SCALE)
    blocks_y = int(HEIGHT/SCALE)

    print(blocks_x,blocks_y)
    # init pygame
    pygame.init()

    # init screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    screen.fill((0, 0, 0))

    all_sprites = sprite.Group()

    
    clock = pygame.time.Clock()
    
    world = World("easy", 5)
    world.startWorld()
    chunk_sprites = []
    for chunk in world.loaded_chunks:
        if chunk:
            chunk_sprites.append(BlockSprite(chunk,blocks_x,blocks_y,SCALE))
            all_sprites.add(chunk_sprites[-1])

    time = 1000
    while 1:
        if time < -500:
            movement = 3
        elif time <= 0:
            time -= 1
            movement = -5.5
        else:
            movement = 3
            time -=1
        clock.tick(144)
        
        if movement > 0 and int(world.moved / (SCALE*16)) >= world.current_chunk:
            _, added = world.loadNextChunk()
            if added:
                chunk_sprites.append(BlockSprite(added,blocks_x,blocks_y,SCALE))
                all_sprites.add(chunk_sprites[-1])
        world.moveWorld(movement)
        for sprite in chunk_sprites:
            sprite.move((-movement,0))

        
                    
        screen.fill("black")
        all_sprites.draw(screen)
        pygame.display.flip()


