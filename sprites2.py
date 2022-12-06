from enum import Enum

import pygame
from pygame.sprite import Sprite

from common import Directions
from spritesheet import SpriteSheet

CELL_SIZE = 64

SPRITE_WIDTH = 80
SPRITE_HEIGHT = 72


class PlayerSprite(pygame.sprite.Sprite):
    __player_sprite = None

    def __init__(self, player, SCALE):
        Sprite.__init__(self)

        PLAYER_SPRITESHEET = SpriteSheet("player.png")

        self.player = player
        self.SCALE = SCALE

        player_image_rect = (0, 0, SPRITE_WIDTH, SPRITE_HEIGHT)
        self.stop_image = PLAYER_SPRITESHEET.image_at(player_image_rect, -1)
        self.stop_image = pygame.transform.scale(self.stop_image, (SCALE, SCALE))

        self.left_move_images = ((0, 2), (1, 2), (2, 2), (3, 2))
        self.left_move_images = [pygame.transform.scale(
            PLAYER_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE, SCALE),
        )
            for a, b in self.left_move_images
        ]
        self.left_move_images.append(0)

        self.right_move_images = ((0, 3), (1, 3), (2, 3), (3, 3))
        self.right_move_images = [pygame.transform.scale(
            PLAYER_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE, SCALE),
        )
            for a, b in self.right_move_images
        ]
        self.right_move_images.append(0)

        self.jump_count = 0  # number of UP actions done for a jump
        self.jump_limit = 60  # max number of UP actions per each jump
        self.jumping = False  # is jumping
        self.falling = False  # is falling

        # to avoid consecutive jumps
        # when the user presses the space key and never lift the finger, the sprite will jump forever :x
        self.jump_again = True

        self.image = self.left_move_images[2]
        self.rect = self.image.get_rect()
        self.rect.y = 500
        PlayerSprite.__player_sprite = self

    @staticmethod
    def get_or_create(**kwargs):
        if PlayerSprite.__player_sprite:
            return PlayerSprite.__player_sprite

        return PlayerSprite(**kwargs)

    def update(self):
        if self.player.direction:
            move_images = None
            if self.player.direction == Directions.LEFT:
                move_images = self.left_move_images
            elif self.player.direction == Directions.RIGHT:
                move_images = self.right_move_images
            elif self.player.direction == Directions.UP:
                if self.jump_count < self.jump_limit and not self.falling and self.jump_again:
                    self.jumping = True
                    self.jump_again = False

            if self.player.direction != Directions.UP:
                x, y = self.player.direction
                self.rect.x += x
                self.rect.y += y

            if move_images:
                next_image = move_images[-1]
                move_images[-1] = (next_image + 1) % 4
                self.image = move_images[next_image]

            self.player.direction = None

        if self.jump_count >= self.jump_limit:
            self.jumping = False
            self.falling = True

        if self.jumping:
            self.rect.y -= 1
            self.jump_count += 1
        elif self.falling:
            self.rect.y += 1
            self.jump_count -= 1
            if self.jump_count <= 0:
                self.falling = False

    def can_jump_again(self):
        if not self.falling and not self.jumping:
            self.jump_again = True
