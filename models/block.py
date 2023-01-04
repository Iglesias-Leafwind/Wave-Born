import json

from sprites.chunk_sprites import EndSprite

#block class that represents a single block in the chunk
class Block:
    def __init__(self, pos, block_type):
        self.x = pos[0]
        self.y = pos[1]
        self.block_type = block_type
        self.broken = False
    #removed feature
    def breakBlock(self):
        self.broken = True

#class chunk that represents a chunk of the world it has
#xpos int- its starting position in the x axis
#blocks [blocks]- all the blocks in this chunk
#pre_Requisits [[int],[int]]- the requisits to enter the chunks
#post_requisits [[int],[int]]- the requisits to exis this chunk
#tunnel boolean- if it is the tunnel or not
class Chunk:
    def __init__(self, xpos, blocks, pre_requisits, post_requisits, tunnel=False, end=False):
        self.x = xpos
        self.blocks = blocks
        for block in self.blocks:
            block.x += self.x

        self.tunnel = tunnel
        self.pre_requisits = pre_requisits
        self.post_requisits = post_requisits
    #if this is the final chunk this method will create the end sprite for this chunk
    def end_chunk(self, SCALE=32):
        self.end_sprite = EndSprite(SCALE)

    #method that will load a chunk from a file and create a chunk object
    @staticmethod
    def load_chunk(xpos,json_file_path,end=False):
                
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
        
        return Chunk(xpos,blocks,pre_requisits,post_requisits,tunnel,end=end)
    #will write the chunk into a file
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
    #will udpate a chunk by moving it x_movement in pixels
    def update(self, x_movement):
        self.x -= x_movement
        for block in self.blocks:
            block.x -= x_movement
    #will check if this chunk can be generated based on post_requists of another chunk
    def can_be_generated(self, post_requisits):
        for possible in self.pre_requisits:
            low_requisit = possible[0]
            top_requisit = possible[1]
            for available in post_requisits:
                if available[0] < top_requisit and available[1] > low_requisit:
                    return True
        return False
