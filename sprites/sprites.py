import pygame
from pygame.sprite import Sprite

from models.common import Directions
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

        # to avoid consecutive jumps
        # when the user presses the space key and never lift the finger, the sprite will jump forever :x
        self.jump_again = True

        self.image = self.stop_image
        self.rect = self.image.get_rect()
        self.rect.y = 500
        self.mask = pygame.mask.from_surface(self.image)
        PlayerSprite.__player_sprite = self

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
    def __init__(self, change_per_frames=0):
        Sprite.__init__(self)
        self.left_move_images = []
        self.right_move_images = []
        self.img_indexes = []
        self.monsters = []
        self.change_per_frames = change_per_frames
        self.count = 0

    def _next_image(self, id, left):
        if left:
            move_images = self.left_move_images
        else:
            move_images = self.right_move_images

        next_index = self.img_indexes[id]
        next_image = move_images[next_index]

        if self.count >= self.change_per_frames:
            self.img_indexes[id] = (next_index + 1) % len(move_images)
            self.count = 0
        else:
            self.count += 1
        return next_image

    def update(self):
        # TODO move randomly
        pass

    def draw(self, mask):
        self.mask = pygame.mask.from_surface(self.image)
        monster_maskSurf = self.mask.to_surface()
        monster_maskSurf.set_colorkey((0, 0, 0, 0))
        olist = self.mask.outline()
        pygame.draw.polygon(monster_maskSurf, (0, 0, 255), olist, 0)

        for i, monster in enumerate(self.monsters):
            mask.blit(
                self._next_image(i, True),
                (monster.pos[0], monster.pos[1]),
            )


class BirdLikeSprite(MonsterSprite):
    __bird_sprite = None

    def __init__(self, birds, SCALE):
        MonsterSprite.__init__(self, 16)

        BIRD_SPRITESHEET = SpriteSheet("sources/imgs/bird.png")
        SPRITE_WIDTH = 91
        SPRITE_HEIGHT = 96

        self.monsters = birds
        self.SCALE = SCALE

        self.left_move_images = [(i, 0) for i in range(9)]
        self.left_move_images = [pygame.transform.scale(
            BIRD_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE, SCALE),
        )
            for a, b in self.left_move_images
        ]

        self.right_move_images = [pygame.transform.flip(mi, True, False) for mi in self.left_move_images]

        self.img_indexes = [0] * len(self.monsters)

        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        BirdLikeSprite.__bird_sprite = self

    def update(self):
        # TODO move randomly
        pass


class SpiderLikeSprite(MonsterSprite):
    __spider_sprite = None

    def __init__(self, spiders, SCALE):
        MonsterSprite.__init__(self)

        SPIDER_SPRITESHEET = SpriteSheet("sources/imgs/spider.png")
        SPRITE_WIDTH = 127
        SPRITE_HEIGHT = 124

        self.monsters = spiders
        self.SCALE = SCALE

        self.left_move_images = [(i, 0) for i in range(13)]
        self.left_move_images = [pygame.transform.scale(
            SPIDER_SPRITESHEET.image_at(
                (a * SPRITE_WIDTH, b * SPRITE_HEIGHT, SPRITE_WIDTH, SPRITE_HEIGHT), -1
            ).convert_alpha(),
            (SCALE, SCALE),
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
        # TODO move randomly
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
            (SCALE, SCALE),
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
        # TODO move randomly
        pass
