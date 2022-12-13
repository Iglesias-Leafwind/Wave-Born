from pygame import *
from sprites.sprites import BlockSprite
from models.block import *

if __name__ == "__main__":
    WIDTH = 1024+64+64
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
    
    blocks = []
    #1 - surface floor 
    #2 - metal floor
    #0 - underground
    #DELETE checking limits
    for line in range(blocks_y-7,blocks_y):
        blocks.append(Block([17*SCALE,line*SCALE],2))
    for line in range(0,blocks_y-3):
        blocks.append(Block([0*SCALE,line*SCALE],2))
    for block in blocks:
        all_sprites.add(BlockSprite(block,SCALE))

    blocks = []
    #adding a metal platform
    #offset = 4*SCALE
    #for col in range(5):
    #    blocks.append(Block([offset+col*SCALE,(blocks_y-6)*SCALE],2))
    #adding blocks
    for col in range(0,14):
        blocks.append(Block([col*SCALE,(blocks_y-3)*SCALE],1))
    for line in range(blocks_y,blocks_y-3,-1):
        for col in range(0,14):
            blocks.append(Block([col*SCALE,line*SCALE],0))

    chunk1 = Chunk(32,blocks,[[0,(blocks_y-3)*SCALE]],[[(blocks_y-7)*SCALE,(blocks_y)*SCALE]])

    blocks = []
    #DELETE checking limits
    for line in range(blocks_y-8,blocks_y-4):
        blocks.append(Block([35*SCALE,line*SCALE],2))
        
    for line in range(blocks_y-13,blocks_y-8):
        blocks.append(Block([18*SCALE,line*SCALE],2))

    for block in blocks:
        all_sprites.add(BlockSprite(block,SCALE))

    blocks = []
    #adding blocks
    for col in range(0,2):
        blocks.append(Block([col*SCALE,(blocks_y-16)*SCALE],1))
        for line in range(blocks_y-14,blocks_y-16,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(2,3):
        blocks.append(Block([col*SCALE,(blocks_y-15)*SCALE],1))
        for line in range(blocks_y-13,blocks_y-15,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(3,4):
        blocks.append(Block([col*SCALE,(blocks_y-15)*SCALE],1))
        for line in range(blocks_y-12,blocks_y-15,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(4,7):
        blocks.append(Block([col*SCALE,(blocks_y-14)*SCALE],1))
        for line in range(blocks_y-10,blocks_y-14,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(7,8):
        blocks.append(Block([col*SCALE,(blocks_y-12)*SCALE],1))
        for line in range(blocks_y-8,blocks_y-12,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(8,10):
        blocks.append(Block([col*SCALE,(blocks_y-15)*SCALE],1))
        for line in range(blocks_y-10,blocks_y-15,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(10,11):
        blocks.append(Block([col*SCALE,(blocks_y-14)*SCALE],1))
        for line in range(blocks_y-9,blocks_y-14,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(11,13):
        blocks.append(Block([col*SCALE,(blocks_y-15)*SCALE],1))
        for line in range(blocks_y-10,blocks_y-15,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(13,14):
        blocks.append(Block([col*SCALE,(blocks_y-16)*SCALE],1))
        for line in range(blocks_y-11,blocks_y-16,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(14,15):
        blocks.append(Block([col*SCALE,(blocks_y-16)*SCALE],1))
        for line in range(blocks_y-12,blocks_y-16,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(15,16):
        blocks.append(Block([col*SCALE,(blocks_y-16)*SCALE],1))
        for line in range(blocks_y-13,blocks_y-16,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
        
    for col in range(0,2):
        for line in range(blocks_y,blocks_y-9,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(2,4):
        for line in range(blocks_y,blocks_y-7,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(4,5):
        for line in range(blocks_y,blocks_y-6,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(5,16):
        for line in range(blocks_y,blocks_y-5,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
            
    chunk2 = Chunk(96+16*32,blocks,[[(blocks_y-13)*SCALE,(blocks_y-8)*SCALE]],[[(blocks_y-8)*SCALE,(blocks_y-4)*SCALE]],True)

    names = ["tunnelEntrance","mountainBridgeLeft","mountainBridgeRight","plane","planeWhole1","planeWhole2","planeWhole3"]
    chunk1 = Chunk.load_chunk(32,"./chunks/normal/tunnelEntrance")
    #chunk2 = Chunk.load_chunk(96+16*32,"./chunks/normal/"+names[1])
    for block in chunk1.blocks:
        all_sprites.add(BlockSprite(block,SCALE))
    for block in chunk2.blocks:
        all_sprites.add(BlockSprite(block,SCALE))
    clock = pygame.time.Clock()
    #chunk1.save_chunk("./chunks/normal/planeWhole3")
    #chunk2.save_chunk("./chunks/tunnel/tunnelTopEntrance2")

    
    

    while 1:
            clock.tick(144)

            all_sprites.draw(screen)
            pygame.display.flip()


