import pygame
from pygame.sprite import Sprite

from sprites.spritesheet import SpriteSheet


class EndSprite(pygame.sprite.Sprite):
    def __init__(self, SCALE):
        Sprite.__init__(self)
        END_CITY_SPRITESHEET = SpriteSheet("sources/imgs/end_city.png")

        self.image = pygame.transform.scale(END_CITY_SPRITESHEET.image_at((0, 0, 160, 180), -1),
                                            (SCALE * 5, SCALE * 5 + SCALE / 5), )

        self.rect = self.image.get_rect()

    def move(self, velocity):
        self.rect.x += velocity[0]
        self.rect.y += velocity[1]


class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, chunk, blocks_x, blocks_y, SCALE):
        Sprite.__init__(self)
        BLOCK_SPRITESHEET = SpriteSheet("sources/imgs/blocks.png")
        self.chunk = chunk
        self.blocks = self.chunk.blocks

        images = [pygame.transform.scale(BLOCK_SPRITESHEET.image_at((SCALE * block.block_type, 0, SCALE, SCALE), -1),
                                         (SCALE, SCALE), ) for block in self.blocks]

        rects = [image.get_rect() for image in images]
        for idx, rect in enumerate(rects):
            rect.x = self.blocks[idx].x
            rect.y = self.blocks[idx].y

        self.rect = rects[0].copy()
        for rect in rects[1:]:
            self.rect.union_ip(rect)

        # Create a new transparent image with the combined size.
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        # Now blit all sprites onto the new surface.
        for idx, image in enumerate(images):
            self.image.blit(image, (rects[idx].x - self.rect.left,
                                    rects[idx].y - self.rect.top))

    def move(self, velocity):
        self.rect.move_ip(velocity)
        try:
            self.chunk.end_sprite.move(velocity)
        except:
            pass

    def remove(self):
        self.kill()
