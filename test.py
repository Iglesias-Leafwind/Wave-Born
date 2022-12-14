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
    
    for chunk in world.loaded_chunks:
        if chunk:
            all_sprites.add(BlockSprite(chunk,blocks_x,blocks_y,SCALE))
    while 1:
            clock.tick(144)
            
            all_sprites.draw(screen)
            pygame.display.flip()


