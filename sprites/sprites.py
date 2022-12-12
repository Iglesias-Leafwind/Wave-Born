import random

import pygame
from pygame.sprite import Sprite

from models.common import Directions
from models.game_objects import Feather
from models.sound import Sound
from sprites.spritesheet import SpriteSheet

CELL_SIZE = 64

ACC = 0.0975


class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, block, SCALE):
        Sprite.__init__(self)
        BLOCK_SPRITESHEET = SpriteSheet("sources/imgs/blocks.png")

        self.block = block
        block_type = block.block_type
        self.image = BLOCK_SPRITESHEET.image_at((SCALE * block_type, 0, SCALE, SCALE), -1)

        self.rect = self.image.get_rect()
        self.rect.x = block.x
        self.rect.y = block.y


class PlayerSprite(pygame.sprite.Sprite):
    __player_sprite = None

    def __init__(self, player, SCALE):
        Sprite.__init__(self)

        PLAYER_SPRITESHEET = SpriteSheet("sources/imgs/player.png")
        SPRITE_WIDTH = 80
        SPRITE_HEIGHT = 72

        self.player = player
        self.SCALE = SCALE

        self.land_sound = Sound("sources/sounds/land.mp3")
        self.jump_sound = Sound("sources/sounds/jump.mp3")
        self.running_sound = Sound("sources/sounds/running.mp3")

        player_image_rect = (0, 0, SPRITE_WIDTH, SPRITE_HEIGHT)

        self.stop_image = PLAYER_SPRITESHEET.image_at(player_image_rect, -1).convert_alpha()
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
        self.left_move_images.append(0)  # index of the current image

        self.right_move_images = ((0, 3), (1, 3), (2, 3), (3, 3))
        self.right_move_images = [pygame.transform.scale(
            PLAYER_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE, SCALE),
        )
            for a, b in self.right_move_images
        ]
        self.right_move_images.append(0)  # index of the current image

        self.jump_count = 0  # number of UP actions done for a jump
        self.jump_limit = 60  # max number of UP actions per each jump
        self.jumping = False  # is jumping
        self.falling = False  # is falling
        self.running = False  # is running
        self.without_moving = 0  # number of updates without moving action
        self.playing_running_sound = True

        # to avoid consecutive jumps
        # when the user presses the space key and never lift the finger, the sprite will jump forever :x
        self.jump_again = True

        self.image = self.stop_image
        self.rect = self.image.get_rect()
        self.rect.y = 500
        self.mask = pygame.mask.from_surface(self.image)
        PlayerSprite.__player_sprite = self

    def has_collision_with(self, x, y):
        return abs(self.rect.x - x) < 16 and abs(self.rect.y - y) < 16

    @staticmethod
    def get_or_create(**kwargs):
        if PlayerSprite.__player_sprite:
            return PlayerSprite.__player_sprite

        return PlayerSprite(**kwargs)

    def draw(self, mask):
        self.mask = pygame.mask.from_surface(self.image)
        player_maskSurf = self.mask.to_surface()
        player_maskSurf.set_colorkey((0, 0, 0, 0))
        olist = self.mask.outline()
        pygame.draw.polygon(player_maskSurf, (0, 0, 255), olist, 0)
        mask.blit(player_maskSurf, (self.rect.x, self.rect.y))

    def _start_jump(self):
        self.jumping = True
        self.jump_again = False
        self.jump_sound.play()

    def _jump(self):
        self.rect.y -= 0.1 - ACC
        self.jump_count += 0.5

    def _fail(self):
        self.rect.y += 1
        self.jump_count -= 0.5
        if self.jump_count <= 0:
            self.falling = False
            self.land_sound.play()
            self.jump_count = 0

    def _update_image(self, move_images):
        if move_images:
            next_image = move_images[-1]
            move_images[-1] = (next_image + 1) % (len(move_images) - 1)
            self.image = move_images[next_image]

    def _check_running(self):
        if not self.player.direction:
            self.without_moving += 1
        else:
            self.without_moving = 0

        if self.without_moving >= 2:
            self.without_moving = 0
            self.running = False

    def _check_jump(self):
        if self.jump_count >= self.jump_limit:
            self.jumping = False
            self.falling = True

    def update(self):
        if self.player.direction:
            move_images = None
            if self.player.direction == Directions.LEFT:
                move_images = self.left_move_images
                self.running = True
            elif self.player.direction == Directions.RIGHT:
                move_images = self.right_move_images
                self.running = True
            elif self.player.direction == Directions.UP:
                if self.jump_count < self.jump_limit and not self.falling and self.jump_again:
                    self._start_jump()
                self.running = False
            else:
                self.running = False

            if self.player.direction != Directions.UP:
                # update the position when the direction is different of UP
                # because when the direction == UP, we will modify the y in the jump method
                x, y = self.player.direction
                self.rect.x += x
                self.rect.y += y

            self._update_image(move_images)

        self._check_running()

        if self.running and not self.playing_running_sound:
            self.running_sound.play(loops=-1)
            self.playing_running_sound = True
        elif not self.running:
            self.playing_running_sound = False
            self.running_sound.stop()

        self._check_jump()

        if self.jumping:
            self._jump()
        elif self.falling:
            self._fail()

        self.player.direction = None

    def can_jump_again(self):
        if not self.falling and not self.jumping:
            self.jump_again = True


class MonsterSprite(pygame.sprite.Sprite):
    def __init__(self, image_update_per_frames=0, pos_update_per_frames=0):
        Sprite.__init__(self)
        self.left_move_images = []
        self.right_move_images = []
        self.img_indexes = []
        self.monsters = []
        self.image_update_per_frames = image_update_per_frames
        self.pos_update_per_frames = pos_update_per_frames
        self.image_update_count = 0
        self.pos_update_count = 0

    def _next_image(self, id, direction):
        if direction == 1:
            move_images = self.right_move_images
        else:
            move_images = self.left_move_images

        next_index = self.img_indexes[id]
        next_image = move_images[next_index]

        if self.image_update_count >= self.image_update_per_frames:
            self.img_indexes[id] = (next_index + 1) % len(move_images)
            self.image_update_count = 0
        else:
            self.image_update_count += 1
        return next_image

    def update(self):
        if self.pos_update_count >= self.pos_update_per_frames:
            for monster in self.monsters:
                old_pos = monster.pos
                new_pos = old_pos[0] + monster.direction, old_pos[1]
                monster.pos = new_pos
            self.pos_update_count = 0
        else:
            self.pos_update_count += 1

    def draw(self, mask):
        self.mask = pygame.mask.from_surface(self.image)
        monster_maskSurf = self.mask.to_surface()
        monster_maskSurf.set_colorkey((0, 0, 0, 0))
        olist = self.mask.outline()
        pygame.draw.polygon(monster_maskSurf, (0, 0, 255), olist, 0)

        for i, monster in enumerate(self.monsters):
            mask.blit(
                self._next_image(i, monster.direction),
                (monster.pos[0], monster.pos[1]),
            )


class FeatherSprite(pygame.sprite.Sprite):
    __feather_sprite = None

    def __init__(self, WIDTH, HEIGHT, SCALE):
        Sprite.__init__(self)
        self.feathers = {}
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.left_image = pygame.image.load("sources/imgs/feather.png").convert_alpha()
        self.left_image = pygame.transform.scale(self.left_image, (SCALE, SCALE))
        self.right_image = pygame.transform.flip(self.left_image, True, False)

        self.image = self.left_image
        self.rect = self.image.get_rect()
        FeatherSprite.__feather_sprite = self

    @staticmethod
    def get_or_create(**kwargs):
        if FeatherSprite.__feather_sprite:
            return FeatherSprite.__feather_sprite
        else:
            return FeatherSprite(**kwargs)

    def add_feather(self, bird_id, feather):
        self.feathers[bird_id] = feather

    def feather_flying(self, bird_id):
        return bird_id in self.feathers

    def draw(self, mask):
        self.mask = pygame.mask.from_surface(self.image)
        monster_maskSurf = self.mask.to_surface()
        monster_maskSurf.set_colorkey((0, 0, 0, 0))
        olist = self.mask.outline()
        pygame.draw.polygon(monster_maskSurf, (0, 0, 255), olist, 0)

        for feather in self.feathers.values():
            mask.blit(
                self._get_image(feather.direction),
                (feather.pos[0], feather.pos[1]),
            )

    def _get_image(self, direction):
        if direction == 1:
            return self.right_image
        return self.left_image

    def _has_collision_or_out_of_world(self, feather_pos, WIDTH, HEIGHT):
        player = PlayerSprite.get_or_create()
        if player.has_collision_with(feather_pos[0], feather_pos[1]) or \
                feather_pos[0] < 0 or feather_pos[0] > WIDTH or feather_pos[1] > HEIGHT:
            return True

    def update(self):
        to_be_removed = []
        for bird_id, feather in self.feathers.items():
            old_pos = feather.pos
            new_pos = old_pos[0] + feather.direction, old_pos[1] + 1
            if self._has_collision_or_out_of_world(new_pos, self.WIDTH, self.HEIGHT):
                to_be_removed.append(bird_id)
            else:
                feather.pos = new_pos

        for i in to_be_removed:
            del self.feathers[i]

class BirdLikeSprite(MonsterSprite):
    __bird_sprite = None

    def __init__(self, birds, WIDTH, HEIGHT, SCALE):
        MonsterSprite.__init__(self, 16, 10)

        BIRD_SPRITESHEET = SpriteSheet("sources/imgs/bird.png")
        self.sprite_width = 92
        self.sprite_height = 96

        self.monsters = birds
        self.SCALE = SCALE
        self.feather_sprite = FeatherSprite.get_or_create(WIDTH=WIDTH, HEIGHT=HEIGHT, SCALE=SCALE)
        self.right_move_images = [(i, 0) for i in range(9)]
        self.right_move_images = [pygame.transform.scale(
            BIRD_SPRITESHEET.image_at(
                (a * self.sprite_width, b * self.sprite_height, self.sprite_width, self.sprite_height), -1
            ).convert_alpha(),
            (SCALE * 2, SCALE * 2),
        )
            for a, b in self.right_move_images
        ]

        self.left_move_images = [pygame.transform.flip(mi, True, False) for mi in self.right_move_images]

        self.img_indexes = [0] * len(self.monsters)

        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        BirdLikeSprite.__bird_sprite = self

    def update(self):
        super(BirdLikeSprite, self).update()
        for bird in self.monsters:
            if not bird.attacking:
                if self._want_attack():
                    bird.attacking = True
                    self.feather_sprite.add_feather(bird.id, Feather(bird.get_center(self.sprite_width, self.sprite_height), bird.direction))
            else:
                bird.attacking = self.feather_sprite.feather_flying(bird.id)

        self.feather_sprite.update()

    def draw(self, mask):
        super(BirdLikeSprite, self).draw(mask)
        self.feather_sprite.draw(mask)

    def _want_attack(self):
        return random.randint(0, 100) > 99


class SpiderLikeSprite(MonsterSprite):
    __spider_sprite = None

    def __init__(self, spiders, SCALE):
        MonsterSprite.__init__(self, 32, 10)

        SPIDER_SPRITESHEET = SpriteSheet("sources/imgs/spider.png")
        SPRITE_WIDTH = 128
        SPRITE_HEIGHT = 124

        self.monsters = spiders
        self.SCALE = SCALE

        self.left_move_images = [(i, 0) for i in range(12)]
        self.left_move_images = [pygame.transform.scale(
            SPIDER_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE * 2, SCALE * 2),
        )
            for a, b in self.left_move_images
        ]

        self.right_move_images = [pygame.transform.flip(mi, True, False) for mi in self.left_move_images]

        self.img_indexes = [0] * len(self.monsters)

        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        SpiderLikeSprite.__spider_sprite = self

    def update(self):
        # TODO move until hit a wall
        super(SpiderLikeSprite, self).update()
        pass


class WhaleSprite(MonsterSprite):
    __whale_sprite = None

    def __init__(self, spiders, SCALE):
        MonsterSprite.__init__(self, 32)

        WHALE_SPRITESHEET = SpriteSheet("sources/imgs/whale.png")
        SPRITE_WIDTH = 133
        SPRITE_HEIGHT = 44

        self.monsters = spiders
        self.SCALE = SCALE

        self.left_move_images = [(0, i) for i in range(7)]
        self.left_move_images = self.left_move_images[::-1]
        self.left_move_images = [pygame.transform.scale(
            WHALE_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE * 20, SCALE * 8),
        )
            for a, b in self.left_move_images
        ]

        self.right_move_images = [pygame.transform.flip(mi, True, False) for mi in self.left_move_images]

        self.img_indexes = [0] * len(self.monsters)

        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        WHALE_SPRITESHEET.__whale_sprite = self

    def update(self):
        # TODO move from left to right unless its end of game which will move from right to left
        # and its laser will destroy blocks
        pass
