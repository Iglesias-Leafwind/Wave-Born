from models.block import Chunk
from os import listdir
from os.path import isfile, join
import random
import copy
import pygame
from sprites.chunk_sprites import BlockSprite

def getPossibleChunks(chunk_list, prev_chunk, check_order):
    requisits = prev_chunk.post_requisits
    for chunk_idx in check_order:
        selected_chunk = chunk_list[chunk_idx]
        if (selected_chunk.can_be_generated(requisits)):
            return selected_chunk
    return None


class World:
    _singleton = None

    def __init__(self, difficulty, time_limit,blocks_x,blocks_y,SCALE):
        self.difficulty = difficulty
        self.time_limit = time_limit*2  # in minutes
        self.num_chunks = int((time_limit * 60) / 8)
        self.start_timer = pygame.time.get_ticks()
        self.font = pygame.font.SysFont('Comic Sans MS', 32)

        self.blocks_x = blocks_x
        self.blocks_y = blocks_y
        self.SCALE = SCALE
        
        self.current_chunk = 0
        self.moved = 0
        self.loaded_chunks = [None, None, None, None, None]
        self.world_chunks = []

        self.generateWorld(self.loadFiles())
        World._singleton = self

    def loadFiles(self):
        self.start = Chunk.load_chunk(0, "./chunks/normal/plane")
        self.end = Chunk.load_chunk(0, "./chunks/normal/plane", end=True)

        file_path = "./chunks/normal"
        normal_chunks = [Chunk.load_chunk(0, join(file_path, f)) for f in listdir(file_path) if
                         isfile(join(file_path, f))]

        file_path = "./chunks/tunnel"
        tunnel_chunks = [Chunk.load_chunk(0, join(file_path, f)) for f in listdir(file_path) if
                         isfile(join(file_path, f))]
        return (normal_chunks, tunnel_chunks)

    def generateWorld(self, chunks):
        normal_qty = [idx for idx in range(len(chunks[0]))]
        tunnel_qty = [idx for idx in range(len(chunks[1]))]
        self.world_chunks.append(self.start)
        for pos in range(1, self.num_chunks - 1):
            if (self.world_chunks[pos - 1].tunnel and random.randint(0, 10)):
                random.shuffle(tunnel_qty)
                next_chunk = getPossibleChunks(chunks[1], self.world_chunks[pos - 1], tunnel_qty)
                if (next_chunk):
                    self.world_chunks.append(copy.deepcopy(next_chunk))
                    continue
            random.shuffle(normal_qty)
            next_chunk = getPossibleChunks(chunks[0], self.world_chunks[pos - 1], normal_qty)
            if (next_chunk):
                self.world_chunks.append(copy.deepcopy(next_chunk))
                continue
            print("Not possible to generate chunks given all possibilities")
            return None
        self.world_chunks.append(self.end)
        
    def startWorld(self):
        self.start_timer = pygame.time.get_ticks()
        for idx, chunk in enumerate(self.world_chunks):
            chunk.update(-idx * 16 * 32)
        for chunk in range(0, 3):
            self.loaded_chunks[chunk + 2] = BlockSprite(self.world_chunks[chunk], self.blocks_x, self.blocks_y, self.SCALE)
            

    def moveWorld(self, move):
        self.moved += move
        for chunk in self.world_chunks:
            chunk.update(move)
            
    def moveCamera(self, move):
        for chunk in self.loaded_chunks:
            try:
                chunk.move((-move, 0))
            except:
                pass
            
    def loadNextChunk(self):
        self.current_chunk += 1
        new_chunk_pos = self.current_chunk + 2

        removed = self.loaded_chunks[0]
        for chunk in range(0, 4):
            self.loaded_chunks[chunk] = self.loaded_chunks[chunk + 1]

        if (new_chunk_pos < len(self.world_chunks)):
            added = BlockSprite(self.world_chunks[new_chunk_pos],self.blocks_x,self.blocks_y,self.SCALE)
            self.loaded_chunks[4] = added
            if new_chunk_pos == (len(self.world_chunks) - 1):
                self.world_chunks[new_chunk_pos].end_sprite.rect.x = 128 + self.world_chunks[new_chunk_pos].x
                self.world_chunks[new_chunk_pos].end_sprite.rect.y = 448 - 180
            return removed, added
        else:
            self.loaded_chunks[4] = None
        return removed, None

    def loadPrevChunk(self):
        self.current_chunk -= 1
        new_chunk_pos = self.current_chunk - 2

        removed = self.loaded_chunks[4]
        for chunk in range(4, 0, -1):
            self.loaded_chunks[chunk] = self.loaded_chunks[chunk - 1]
        
        if (new_chunk_pos > 0):
            added = BlockSprite(self.world_chunks[new_chunk_pos],self.blocks_x,self.blocks_y,self.SCALE)
            self.loaded_chunks[0] = added
            return removed, added
        else:
            self.loaded_chunks[0] = None
        return removed, None

    def get_blocks(self) -> list[BlockSprite]:
        return [w for w in self.loaded_chunks if w]

    @classmethod
    def get_or_create(cls, **kwargs):
        if cls._singleton:
            return cls._singleton
        return cls(**kwargs)

    def get_passed_seconds(self):
        return ((pygame.time.get_ticks()-self.start_timer)/1000)

    def get_passed_time_string(self):
        time_passed = self.get_passed_seconds()
        time_left = self.time_limit*60 - time_passed
        minutes, seconds = divmod(time_left, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        return f'{minutes:02d}:{seconds:02d}'
    
    def get_time_passed_surface(self):
        return self.font.render(self.get_passed_time_string(),False,(255,255,255))

    def timeout(self):
        return self.get_passed_seconds() > (self.time_limit*60)
