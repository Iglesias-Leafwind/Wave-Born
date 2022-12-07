import pygame


class Block():
    def __init__(self, pos, block_type):
        self.x = pos[0]
        self.y = pos[1]
        self.block_type = block_type
        self.broken = False

    def breakBlock(self):
        self.broken = True


class Chunk():
    def __init__(self, xpos, blocks, pre_requisits, post_requisits, tunnel=False, player_height=128):
        self.x = xpos
        self.blocks = blocks

        for block in self.blocks:
            block.x += self.x

        self.tunnel = tunnel
        self.pre_requisits = pre_requisits
        self.post_requisits = post_requisits
        self.player_height = player_height

    def load_chunk(json_file_path):
        return Chunk()

    def update(self, x_movement):
        self.x -= x_movement
        for block in self.blocks:
            block.x -= x_movement

    def can_be_generated(self, post_requisits):
        for possible in self.pre_requisits:
            low_requisit = possible[0]
            top_requisit = possible[1]
            for available in post_requisits:
                if available[0] < top_requisit and available[1] > low_requisit:
                    return True
        return False

if __name__ == "__main__":
    from pygame import *
    from pygame.sprite import *
    from sprites import BlockSprite
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
    for line in range(blocks_y-8,blocks_y-3):
        blocks.append(Block([17*SCALE,line*SCALE],2))
    for line in range(0,blocks_y-3):
        blocks.append(Block([0*SCALE,line*SCALE],2))
    for block in blocks:
        all_sprites.add(BlockSprite(block,SCALE))

    blocks = []
    #adding a metal platform
    offset = 4*SCALE
    for col in range(5):
        blocks.append(Block([offset+col*SCALE,(blocks_y-6)*SCALE],2))
    #adding blocks
    for col in range(0,16):
        blocks.append(Block([col*SCALE,(blocks_y-3)*SCALE],1))
    for line in range(blocks_y,blocks_y-3,-1):
        for col in range(0,16):
            blocks.append(Block([col*SCALE,line*SCALE],0))

    chunk1 = Chunk(32,blocks,[[0,(blocks_y-3)*SCALE]],[[(blocks_y-8)*SCALE,(blocks_y-3)*SCALE]])

    blocks = []
    #DELETE checking limits
    for line in range(blocks_y-16,blocks_y-11):
        blocks.append(Block([35*SCALE,line*SCALE],2))
    for line in range(0,blocks_y-5):
        blocks.append(Block([18*SCALE,line*SCALE],2))
    for block in blocks:
        all_sprites.add(BlockSprite(block,SCALE))

    blocks = []
    #adding blocks
    for col in range(0,3):
        blocks.append(Block([col*SCALE,(blocks_y-5)*SCALE],1))
    for line in range(blocks_y,blocks_y-5,-1):
        for col in range(0,3):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(3,7):
        for line in range(blocks_y,blocks_y-col-(col-2)-1,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(3,7):
        blocks.append(Block([col*SCALE,(blocks_y-col-(col-2)-1)*SCALE],1))
        for line in range(blocks_y,blocks_y-col-(col-2)-1,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    for col in range(9,11):
        blocks.append(Block([col*SCALE,(blocks_y-11)*SCALE],1))
        for line in range(blocks_y,blocks_y-11,-1):
            blocks.append(Block([col*SCALE,line*SCALE],0))
    #adding metal bridge
    for col in range(11,16):
        blocks.append(Block([col*SCALE,(blocks_y-11)*SCALE],2))

    blocks.append(Block([11*SCALE,(blocks_y-9)*SCALE],2))
    blocks.append(Block([12*SCALE,(blocks_y-10)*SCALE],2))
    
    chunk2 = Chunk(96+16*32,blocks,[[0,(blocks_y-5)*SCALE]],[[(blocks_y-16)*SCALE,(blocks_y-11)*SCALE]])

    for block in chunk1.blocks:
        all_sprites.add(BlockSprite(block,SCALE))
    for block in chunk2.blocks:
        all_sprites.add(BlockSprite(block,SCALE))
    print(chunk1.can_be_generated(chunk2.post_requisits))
    print(chunk2.can_be_generated(chunk1.post_requisits))
    clock = pygame.time.Clock()
    
while 1:
        clock.tick(144)

        all_sprites.draw(screen)
        pygame.display.flip()

