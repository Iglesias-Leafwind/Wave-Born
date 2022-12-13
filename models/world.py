import pygame
import json
from block import Chunk
from os import listdir
from os.path import isfile, join
import random
import copy

def getPossibleChunks(chunk_list,prev_chunk,check_order):
    requisits = prev_chunk.post_requisits
    for chunk_idx in check_order:
        selected_chunk = chunk_list[chunk_idx]
        if(selected_chunk.can_be_generated(requisits)):
            return selected_chunk
    return None
        
class World():
    def __init__(self, difficulty, time_limit):
        self.difficulty = difficulty
        self.time_limit = time_limit #in minutes
        self.num_chunks = int((time_limit*60)/8)
        
        self.current_chunk = 0
        self.moved = 0
        self.loaded_chunks = []
        self.world_chunks = []
        self.generateWorld(self.loadFiles())

    def loadFiles(self):
        file_path = "./../chunks/normal"
        normal_chunks = [Chunk.load_chunk(0,join(file_path,f)) for f in listdir(file_path) if isfile(join(file_path, f))]
        
        file_path = "./../chunks/tunnel"
        tunnel_chunks = [Chunk.load_chunk(0,join(file_path,f)) for f in listdir(file_path) if isfile(join(file_path, f))]
        return (normal_chunks,tunnel_chunks)

    def generateWorld(self,chunks):
        normal_qty = [idx for idx in range(len(chunks[0]))]
        tunnel_qty = [idx for idx in range(len(chunks[1]))]
        self.world_chunks.append(copy.deepcopy(chunks[0][random.randint(0,len(chunks[0])-1)]))
        for pos in range(1,self.num_chunks):
            if(self.world_chunks[pos-1].tunnel and random.randint(0,10)):
                random.shuffle(tunnel_qty)
                next_chunk = getPossibleChunks(chunks[1],self.world_chunks[pos-1],tunnel_qty)
                if(next_chunk):
                    self.world_chunks.append(copy.deepcopy(next_chunk))
                    continue
            random.shuffle(normal_qty)
            next_chunk = getPossibleChunks(chunks[0],self.world_chunks[pos-1],normal_qty)
            if(next_chunk):
                self.world_chunks.append(copy.deepcopy(next_chunk))
                continue
            print("Not possible to generate chunks given all possibilities")
            return None

    def startWorld(self):
        for chunk in range(0,3):
            self.loaded_chunks.append(self.world_chunks[chunk])
            self.loaded_chunks[chunk].update(-chunk*16*32)
    
    def moveWorld(self,move):
        self.moved += move
        for chunk in self.loaded_Chunks:
            chunk.update(move)

    def loadNextChunk(self):
        self.current_chunk += 1
        new_chunk_pos = self.current_chunk+2
        if(new_chunk_pos < len(self.world_chunks)):
            self.loaded_chunks.append(self.world_chunks[new_chunk_pos])
            self.loaded_chunks[chunk].update(-new_chunk_pos*16*32+self.moved)
            
    def loadPrevChunk(self):
        self.current_chunk -= 1
        new_chunk_pos = self.current_chunk-2
        if(new_chunk_pos > 0):
            self.loaded_chunks.append(self.world_chunks[new_chunk_pos])
            self.loaded_chunks[chunk].update(-new_chunk_pos*16*32+self.moved)
