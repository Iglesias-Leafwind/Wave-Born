from models.block import Chunk
from os import listdir
from os.path import isfile, join
import random
import copy
import pygame
from sprites.chunk_sprites import BlockSprite

#This method will get all possible chunks that can be generated from a list
# "chunk_list" (its a list of possible chunks) based on the parameters of the "prev_chunk"
# the chunk that wants to generate a new one based on a order "check_order"
#chunk_list is a list of chunk objects
#prev_chunk is a chunk object
#check_order is a list of integers representing indexes of chunk_list
def getPossibleChunks(chunk_list, prev_chunk, check_order):
    requisits = prev_chunk.post_requisits
    for chunk_idx in check_order:
        selected_chunk = chunk_list[chunk_idx]
        if (selected_chunk.can_be_generated(requisits)):
            return selected_chunk
    return None

#world class is a singleton that represents the world
class World:
    _singleton = None

    #creates the base world
    #(the size on screen and how many blocks x and y wide as well as the scale of each block)
    def __init__(self, blocks_x, blocks_y, SCALE):
        self.blocks_x = blocks_x
        self.blocks_y = blocks_y
        self.SCALE = SCALE
        
        self.file_chunks = self.loadFiles()
        
        World._singleton = self

    #will load files from 2 paths where it can be a normal chunk or a tunnel chunk
    #this after preloading all the files will store them for future use so we can generate worlds
    #extremely fast
    def loadFiles(self):
        self.start_end_chunk = Chunk.load_chunk(0, "./chunks/normal/plane")

        file_path = "./chunks/normal"
        normal_chunks = [Chunk.load_chunk(0, join(file_path, f)) for f in listdir(file_path) if
                         isfile(join(file_path, f))]

        file_path = "./chunks/tunnel"
        tunnel_chunks = [Chunk.load_chunk(0, join(file_path, f)) for f in listdir(file_path) if
                         isfile(join(file_path, f))]
        return (normal_chunks, tunnel_chunks)

    #this is used to generate a new world each time we start a new game
    #based on a difficulty and time_limit
    #time_limit will determine the size of the world
    #difficulty - int - that determines the number of monster that can be spawned on this world
    #time_limit - int - that determines the size of the world and how much time we have to complete the world
    def generateWorld(self, difficulty, time_limit):
        self.difficulty = difficulty
        self.time_limit = time_limit*2  # in minutes
        self.num_chunks = int((time_limit * 60) / 8)
        self.start_timer = pygame.time.get_ticks()
        self.font = pygame.font.SysFont('Comic Sans MS', 32)
        self.current_chunk = 0
        self.moved = 0
        self.loaded_chunks = [None, None, None, None, None]
        self.world_chunks = []
        self.end_sprite = None
        self.num_monsters = difficulty*2 + 3

        chunks = self.file_chunks
        normal_qty = [idx for idx in range(len(chunks[0]))]
        tunnel_qty = [idx for idx in range(len(chunks[1]))]
        self.world_chunks.append(copy.deepcopy(self.start_end_chunk))
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
        end_chunk = copy.deepcopy(self.start_end_chunk)
        end_chunk.end_chunk()
        self.world_chunks.append(end_chunk)

    #will start the timer of the world and start loading the chunks taht will be represented
    def startWorld(self):
        self.start_timer = pygame.time.get_ticks()
        for idx, chunk in enumerate(self.world_chunks):
            chunk.update(-idx * 16 * 32)
        for chunk in range(0, 3):
            self.loaded_chunks[chunk + 2] = BlockSprite(self.world_chunks[chunk], self.blocks_x, self.blocks_y, self.SCALE)
            
    #this method moves ("move" pixels) to everychunk so that the world moves llike a conveyor belt
    def moveWorld(self, move):
        self.moved += move
        for chunk in self.world_chunks:
            chunk.update(move)
    #this method moves the camera moveing the world but only the 5 chunks that are being loaded
    def moveCamera(self, move):
        for chunk in self.loaded_chunks:
            try:
                chunk.move((-move, 0))
            except:
                pass
    #this method will load the next chunk of the loaded chunks and return the last removed chunk and the last added chunk
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
                self.end_sprite = self.world_chunks[new_chunk_pos].end_sprite
            return removed, added
        else:
            self.loaded_chunks[4] = None
        return removed, None
    #this method will load the prev chunk of the loaded chunks and return the removed and added chunks
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
    #this method returns all blocks that are being loaded
    def get_blocks(self) -> list[BlockSprite]:
        return [w for w in self.loaded_chunks if w]
    #get or create the singleton
    @classmethod
    def get_or_create(cls, **kwargs):
        if cls._singleton:
            return cls._singleton
        return cls(**kwargs)
    #see how many seconds have passed in the timer
    def get_passed_seconds(self):
        return ((pygame.time.get_ticks()-self.start_timer)/1000)
    #get the remaining time as a string
    def get_passed_time_string(self):
        time_passed = self.get_passed_seconds()
        time_left = self.time_limit*60 - time_passed
        minutes, seconds = divmod(time_left, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        return f'{minutes:02d}:{seconds:02d}'
    #get a surface of the remaining time so it can be represented on screen
    def get_time_passed_surface(self):
        return self.font.render(self.get_passed_time_string(),False,(255,255,255))
    #check if the timelimit has reached 0:00
    def timeout(self):
        return self.get_passed_seconds() > (self.time_limit*60)
