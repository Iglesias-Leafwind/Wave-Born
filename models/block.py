import pygame
import json

class Block:
    def __init__(self, pos, block_type):
        self.x = pos[0]
        self.y = pos[1]
        self.block_type = block_type
        self.broken = False

    def breakBlock(self):
        self.broken = True


class Chunk:
    def __init__(self, xpos, blocks, pre_requisits, post_requisits, tunnel=False):
        self.x = xpos
        self.blocks = blocks

        for block in self.blocks:
            block.x += self.x

        self.tunnel = tunnel
        self.pre_requisits = pre_requisits
        self.post_requisits = post_requisits
    
    @staticmethod
    def load_chunk(xpos,json_file_path):
                
        # Opening JSON file
        f = open(json_file_path)
          
        # returns JSON object as 
        # a dictionary
        data = json.load(f)
          
        blocks = []
        
        for block in data["blocks"]:
            blocks.append(Block(block["pos"],block["block_type"]))
        pre_requisits = data["pre_requisits"]
        post_requisits = data["post_requisits"]
        tunnel = data["tunnel"] 

        # Closing file
        f.close()
        
        return Chunk(xpos,blocks,pre_requisits,post_requisits,tunnel)

    def save_chunk(self,json_file_path):
        # Data to be written
        dictionary = {}
        dictionary["blocks"] = [{"pos":(block.x,block.y),"block_type":block.block_type} for block in self.blocks]
        dictionary["pre_requisits"] = self.pre_requisits
        dictionary["post_requisits"] = self.post_requisits
        dictionary["tunnel"] = self.tunnel
        
        # Serializing json
        json_object = json.dumps(dictionary, indent=4)
         
        # Writing to sample.json
        with open(json_file_path, "w") as outfile:
            outfile.write(json_object)     

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
