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
    def __init__(self, pos, blocks, pre_requisits, post_requisits, tunnel=False, player_height=128):
        self.x = pos[0]
        self.y = pos[1]
        self.blocks = blocks
        self.tunnel = tunnel
        self.pre_requisits = pre_requisits
        self.post_requisits = post_requisits
        self.player_height = player_height

    def update(self,x_movement):
        self.x -= x_movement
        for block in self.blocks:
            block.x -= x_movement

    def can_be_generated(self,post_requisits):
        for possible in self.pre_requisits:
            low_requisit = possible[0] + self.player_height
            top_requisit = possible[1] - self.player_height
            for available in post_requisits:
                if(available[0] < top_requisit and available[1] > low_requisit):
                    return True
        return False
