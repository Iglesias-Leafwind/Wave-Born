import random
import time

import pygame
from pygame.sprite import Sprite

from models.common import Directions
from models.sound import Sound
from sprites.spritesheet import SpriteSheet
from sprites.utils import load_images

from models.wave import Wave, Waves

CELL_SIZE = 64
ACC = 0.0975


class PlayerSprite(pygame.sprite.Sprite):
    __player_sprite = None

    def __init__(self, player, enemies, SCALE):
        Sprite.__init__(self)

        PLAYER_SPRITESHEET = SpriteSheet("sources/imgs/player.png")
        SPRITE_WIDTH = 80
        SPRITE_HEIGHT = 72

        self.enemies = enemies
        self.player = player
        self.SCALE = SCALE

        self.land_sound = Sound("sources/sounds/land.mp3")
        self.jump_sound = Sound("sources/sounds/jump.mp3")
        self.running_sound = Sound("sources/sounds/running.mp3")

        self.stop_image = load_images(PLAYER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT, (SCALE, SCALE), [(0, 0)])[0]

        self.left_move_images = ((0, 2), (1, 2), (2, 2), (3, 2))
        self.left_move_images = load_images(PLAYER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT, (SCALE, SCALE),
                                            self.left_move_images)
        self.left_move_images.append(0)  # index of the current image

        self.right_move_images = ((0, 3), (1, 3), (2, 3), (3, 3))
        self.right_move_images = load_images(PLAYER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT, (SCALE, SCALE),
                                             self.right_move_images)
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
        self.rect.x = player.x
        self.rect.y = player.y
        self.pos_before_jump = self.rect.y
        self.mask = pygame.mask.from_surface(self.image)
        PlayerSprite.__player_sprite = self

    def has_collision_with(self, rect):
        return self.rect.colliderect(rect)

    def stepped_on(self, monster_rect):
        if self.has_collision_with(monster_rect) and self.falling and self.rect.y < monster_rect.y:
            return True

    @property
    def pos(self):
        return self.rect.x, self.rect.y

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    def dead(self):
        self.player.dead = True

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

    def _start_jump(self, stepped=False):
        self.jumping = True
        self.falling = False
        self.jump_again = False
        if not stepped:
            self.jump_sound.play()
            self.jump_count = 0
        else:
            self.jump_count = int(self.jump_limit * 0.7)

    def _jump(self):
        self.rect.y -= 0.1 - ACC
        self.jump_count += 0.5

    def _fail(self):
        self.rect.y += 1
        if self.rect.y >= self.pos_before_jump:
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

    def update_camera_movement(self, movement):
        self.rect.x -= movement

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

            if(self.running and not self.falling and not self.jumping):
                if random.randint(0,5) == 5:
                    wave = Wave([self.rect.x+self.SCALE/2, self.rect.y+self.SCALE],
                            random.randint(5, 10), 144,
                                    [0, 0.08])
                    Waves.get_or_create().add_wave(wave)

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

        self.check_collision()

        self.player.direction = None

    def can_jump_again(self):
        if not self.falling and not self.jumping:
            self.jump_again = True

    def check_collision(self):
        for enemy in self.enemies:
            enemy_sprite = enemy.get_or_create()
            for monster in enemy_sprite.monsters:
                if not monster.dying and self.stepped_on(enemy_sprite.rects[monster.id]):
                    enemy_sprite.change_monster_state(monster)
                    monster.dead()
                    self._start_jump(stepped=True)
                elif not monster.dying and self.has_collision_with(enemy_sprite.rects[monster.id]):
                    self.dead()
                    return
