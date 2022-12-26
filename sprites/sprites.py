import random
import time

import pygame
from pygame.sprite import Sprite

from models.common import Directions
from models.game_objects import Feather, Wave, SpiderLike, TurtleLike, Waves
from models.sound import Sound
from sprites.spritesheet import SpriteSheet

CELL_SIZE = 64
ACC = 0.0975

class BackgroundSprite(pygame.sprite.Sprite):
    def __init__(self, leftX=0, leftY=0, width=800, height=600):
        Sprite.__init__(self)
        picture = pygame.image.load("sources/imgs/background.png")
        picture = pygame.transform.scale(picture, (width, height))
        self.image = picture.convert_alpha()

        self.rect = pygame.Rect(leftX, leftY, width - 3, height - 3)

        self.yes = True

    def move(self, x=True, forward=True):
        forward = 1 if forward else -1
        if x:
            self.rect.x += forward * 10
        else:
            self.rect.y += forward * 10

    def update(self, vector=0):
        if vector == 0:
            return
        x, y = vector
        self.rect = self.rect.move(x, y)


    
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

    def remove(self):
        self.kill()


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

    def has_collision_with(self, x, y):
        return abs(self.rect.x - x) < 32 and abs(self.rect.y - y) < 16

    def stepped_on(self, x, y):
        if self.has_collision_with(x, y) and self.falling and self.rect.y < y:
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
            enemy_sprite: MonsterSprite = enemy.get_or_create()
            for monster in enemy_sprite.monsters:
                if not monster.dying and self.stepped_on(monster.pos[0], monster.pos[1]):
                    enemy_sprite.change_monster_state(monster)
                    monster.dead()
                    self._start_jump(stepped=True)
                elif not monster.dying and self.has_collision_with(monster.pos[0], monster.pos[1]):
                    self.dead()
                    return


class MonsterSprite(pygame.sprite.Sprite):
    _single_ton = None

    def __init__(self, image_update_per_frames=0, pos_update_per_frames=0):
        Sprite.__init__(self)
        self.monsters: list
        self.left_move_images: list
        self.right_move_images: list
        self.img_indexes: dict
        self.left_dead_images: list
        self.right_dead_images: list
        self.left_attack_images: list
        self.right_attack_images: list
        self.image_update_per_frames = image_update_per_frames
        self.pos_update_per_frames = pos_update_per_frames
        self.image_update_count = 0
        self.pos_update_count = 0

    def _init_images(self):
        raise NotImplemented

    def change_monster_state(self, monster):
        self.img_indexes[monster.id] = 0

    @classmethod
    def get_or_create(cls, **kwargs):
        if cls._single_ton:
            return cls._single_ton
        return cls(**kwargs)

    def _next_image(self, monster):
        id = monster.id
        indexes = self.img_indexes

        if monster.dying:
            if monster.direction == 1:
                images = self.right_dead_images
            else:
                images = self.left_dead_images
        elif monster.attacking:
            if monster.direction == 1:
                images = self.right_attack_images
            else:
                images = self.left_attack_images
        else:
            if monster.direction == 1:
                images = self.right_move_images
            else:
                images = self.left_move_images
            indexes = self.img_indexes

        next_index = indexes[id]
        next_image = images[next_index]

        if self.image_update_count >= self.image_update_per_frames:
            indexes[id] = (next_index + 1) % len(images)
        return next_image

    def _remove_monster(self, monster):
        self.monsters.remove(monster)
        id = monster.id
        if id in self.img_indexes:
            self.img_indexes.pop(id)

    def update(self):
        if self.pos_update_count >= self.pos_update_per_frames:
            for monster in self.monsters:
                if not monster.dying:
                    monster.update(player_pos=PlayerSprite.get_or_create().pos)
                    """
                    if monster.jumping:
                        monster.jump()
                    elif monster.falling:
                        monster.fail()
                    else:
                        monster.move()
                    """

            self.pos_update_count = 0
        else:
            self.pos_update_count += 1

    def draw(self, mask):
        self.image_update_count += 1
        for monster in self.monsters:
            mask.blit(
                self._next_image(monster),
                (monster.x, monster.y),
            )
        if self.image_update_count >= self.image_update_per_frames:
            self.image_update_count = 0


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
        if player.has_collision_with(feather_pos[0], feather_pos[1]):
            player.dead()
            return True
        if feather_pos[0] < 0 or feather_pos[0] > WIDTH or feather_pos[1] > HEIGHT:
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
    def __init__(self, birds, WIDTH, HEIGHT, SCALE):
        MonsterSprite.__init__(self, 16, 10)

        self.sprite_width = 92
        self.sprite_height = 96

        self.width = WIDTH
        self.height = HEIGHT

        self.monsters = birds
        self.cry_count = {}
        self.cry_interval = 6
        self.cry_sound_path = 'sources/sounds/bird.mp3'
        self.SCALE = SCALE
        self.feather_sprite = FeatherSprite.get_or_create(WIDTH=WIDTH, HEIGHT=HEIGHT, SCALE=SCALE)

        self._init_images()
        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        BirdLikeSprite._single_ton = self

    def _init_images(self):
        BIRD_SPRITESHEET = SpriteSheet("sources/imgs/bird.png")
        self.right_move_images = [(i, 0) for i in range(9)]
        self.right_move_images = load_images(BIRD_SPRITESHEET, self.sprite_width, self.sprite_height,
                                             (self.SCALE * 2, self.SCALE * 2),
                                             self.right_move_images)
        self.left_move_images = invert_images(self.right_move_images)

        self.left_attack_images = self.left_move_images
        self.right_attack_images = self.right_move_images

        self.right_dead_images = self.left_dead_images = self.left_move_images[:1]
        self.img_indexes = {m.id: 0 for m in self.monsters}

    def _remove_monster(self, bird):
        super(BirdLikeSprite, self)._remove_monster(bird)
        if bird.id in self.cry_count:
            cry_sound = self.cry_count[bird.id]['sound']
            cry_sound.stop()
            Sound.pop_sound(cry_sound)
            self.cry_count.pop(bird.id)

    def update(self):
        super(BirdLikeSprite, self).update()

        for bird in self.monsters:
            if bird.is_dead:
                self._remove_monster(bird)
                continue
            else:
                if bird.attacking and not self.feather_sprite.feather_flying(bird.id):
                    self.feather_sprite.add_feather(bird.id,
                                                    Feather(bird.get_center(self.sprite_width, self.sprite_height),
                                                            bird.direction))

            finished_crying = bird.id in self.cry_count and time.time() - self.cry_count[bird.id][
                'time'] >= self.cry_interval

            if finished_crying or bird.id not in self.cry_count:
                if bird.want_cry():
                    if bird.id not in self.cry_count:
                        # first time
                        self.cry_count[bird.id] = {'sound': Sound(self.cry_sound_path),
                                                   'time': time.time(),
                                                   'finished': 0,
                                                   'wait': random.randint(1, self.cry_interval)}
                        self.cry_count[bird.id]['sound'].play()

                        wave = Wave([bird.x, bird.y], random.randint(5, 10), 144,
                                    [0, self.cry_count[bird.id]['wait'] / 10])
                        Waves.get_or_create().add_wave(wave)

                    elif finished_crying:
                        bird_cry = self.cry_count[bird.id]
                        if bird_cry['finished'] == 0:
                            # just finished crying
                            # has to wait for random seconds
                            bird_cry['finished'] = time.time()
                        elif time.time() - bird_cry['finished'] >= bird_cry['wait']:
                            # finished waiting for random seconds
                            # set finished to 0 and cry again
                            wave = Wave([bird.x, bird.y], random.randint(5, 10), 144,
                                        [0, bird_cry['wait'] / 10])
                            Waves.get_or_create().add_wave(wave)
                            bird_cry['time'] = time.time()
                            bird_cry['sound'].play()
                            bird_cry['finished'] = 0

        self.feather_sprite.update()

    def draw(self, mask):
        super(BirdLikeSprite, self).draw(mask)
        self.feather_sprite.draw(mask)


class GroundMonsterSprite(MonsterSprite):
    def update(self):
        super(GroundMonsterSprite, self).update()
        for monster in self.monsters:
            if monster.is_dead:
                continue
            elif monster.dying:
                if self.img_indexes[monster.id] == len(self.left_dead_images) - 1:
                    monster.is_dead = True
            elif monster.attacking and self.img_indexes[monster.id] == len(self.left_attack_images) - 1:
                self.change_monster_state(monster)


class SpiderLikeSprite(GroundMonsterSprite):
    def __init__(self, spiders, WIDTH, HEIGHT, SCALE):
        MonsterSprite.__init__(self, 32, 10)

        self.monsters: list[SpiderLike] = spiders
        self.cry_interval = 10
        self.cry_count = {}
        self.SCALE = SCALE
        self.width = WIDTH
        self.height = HEIGHT
        self._init_images()
        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        SpiderLikeSprite._single_ton = self

    def _init_images(self):
        SPIDER_SPRITESHEET = SpriteSheet("sources/imgs/spider.png")
        SPRITE_WIDTH = 128
        SPRITE_HEIGHT = 124

        self.left_move_images = [(i, 0) for i in range(12)]
        self.left_move_images = load_images(SPIDER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            self.left_move_images)

        self.left_dead_images = [(i, 0) for i in range(16, 23)]
        self.left_dead_images = load_images(SPIDER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            self.left_dead_images)

        self.right_move_images = invert_images(self.left_move_images)
        self.right_dead_images = invert_images(self.left_dead_images)

        self.left_attack_images = load_images(SPIDER_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                              (self.SCALE * 2, self.SCALE * 2),
                                              [(i, 0) for i in range(12, 17)])

        self.right_attack_images = invert_images(self.left_attack_images)

        self.img_indexes = {m.id: 0 for m in self.monsters}

    def update(self):
        super(SpiderLikeSprite, self).update()
        for spider in self.monsters:
            if spider.is_dead:
                self._remove_monster(spider)


class TurtleLikeSprite(GroundMonsterSprite):
    def __init__(self, turtles, WIDTH, HEIGHT, SCALE):
        MonsterSprite.__init__(self, 25, 10)

        self.monsters: list[TurtleLike] = turtles
        self.SCALE = SCALE
        self.width = WIDTH
        self.height = HEIGHT
        self.sound_count = {}
        self.cry_interval = 6
        self.cry_sound_path = 'sources/sounds/turtle.mp3'
        self.step_sound_path = 'sources/sounds/step.mp3'
        self._init_images()
        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        TurtleLikeSprite._single_ton = self

    def _init_images(self):
        TURTLE_SPRITESHEET = SpriteSheet("sources/imgs/tortoise.png")
        SPRITE_WIDTH = 33
        SPRITE_HEIGHT = 42

        self.left_move_images = load_images(TURTLE_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            [(i, 0) for i in range(3)])

        self.left_dead_images = load_images(TURTLE_SPRITESHEET, 35, 42,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            [(i, 3) for i in range(4)])

        self.right_move_images = invert_images(self.left_move_images)
        self.right_dead_images = invert_images(self.left_dead_images)

        self.left_attack_images = load_images(TURTLE_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                              (self.SCALE * 2, self.SCALE * 2),
                                              [(i, 2) for i in range(3)])

        self.right_attack_images = invert_images(self.left_attack_images)

        self.img_indexes = {m.id: 0 for m in self.monsters}

    def _remove_monster(self, turtle):
        super(TurtleLikeSprite, self)._remove_monster(turtle)
        if turtle.id in self.sound_count:
            step_sound = self.sound_count[turtle.id]['step']
            step_sound.stop()
            Sound.pop_sound(step_sound)
            cry_sound = self.sound_count[turtle.id]['cry']
            cry_sound.stop()
            Sound.pop_sound(cry_sound)
            self.sound_count.pop(turtle.id)

    def update(self):
        super(TurtleLikeSprite, self).update()
        for turtle in self.monsters:
            if turtle.is_dead:
                self._remove_monster(turtle)
                continue

            if turtle.id not in self.sound_count:
                self.sound_count[turtle.id] = {'step': Sound(self.step_sound_path),
                                               'cry': Sound(self.cry_sound_path),
                                               'time': 1 << 31,
                                               'finished': 0,
                                               "wait": random.randint(1, self.cry_interval)}

            finished_crying = time.time() - self.sound_count[turtle.id]['time'] >= self.cry_interval

            if not turtle.dying and not turtle.attacking:
                if turtle.want_cry():
                    if self.sound_count[turtle.id]['time'] == 1 << 31:
                        # first time
                        self.sound_count[turtle.id]['time'] = time.time()
                        self.sound_count[turtle.id]['cry'].play()
                        Waves.get_or_create().add_wave(Wave([turtle.x, turtle.y], random.randint(1, 5), 144,
                                                            [0, self.sound_count[turtle.id]['wait'] / 5]))
                    elif finished_crying:
                        turtle_cry = self.sound_count[turtle.id]
                        if turtle_cry['finished'] == 0:
                            # just finished crying
                            # has to wait for random seconds
                            turtle_cry['finished'] = time.time()
                        elif time.time() - turtle_cry['finished'] >= turtle_cry['wait']:
                            # finished waiting for random seconds
                            # set finished to 0 and cry again
                            turtle_cry['time'] = time.time()
                            turtle_cry['cry'].play()
                            Waves.get_or_create().add_wave(Wave([turtle.x, turtle.y], random.randint(1, 5), 144,
                                                                [0, turtle_cry['wait'] / 5]))
                            turtle_cry['finished'] = 0

            if turtle.dying or turtle.attacking:
                self.sound_count[turtle.id]['step'].stop()
            else:
                self.sound_count[turtle.id]['step'].play(loops=-1)


class WhaleSprite(MonsterSprite):
    def __init__(self, whales, SCALE):
        MonsterSprite.__init__(self, 100, 128)
        self.monsters = whales
        self.attack_count = {}
        self.attack_interval = 5  # 10s
        self.cry_sound_path = "sources/sounds/whale.mp3"
        self.SCALE = SCALE
        self._init_images()
        self.image = self.left_move_images[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        WhaleSprite._single_ton = self

    def _init_images(self):
        WHALE_SPRITESHEET = SpriteSheet("sources/imgs/whale.png")
        SPRITE_WIDTH = 133
        SPRITE_HEIGHT = 44

        self.left_move_images = [(0, i) for i in range(7)]
        self.left_move_images = self.left_move_images[::-1]
        self.left_move_images = load_images(WHALE_SPRITESHEET, SPRITE_WIDTH, SPRITE_HEIGHT,
                                            (self.SCALE * 20, self.SCALE * 8), self.left_move_images)
        self.right_move_images = invert_images(self.left_move_images)
        self.left_attack_images = load_images(WHALE_SPRITESHEET, SPRITE_WIDTH, 43,
                                              (self.SCALE * 20, self.SCALE * 8), [(1, 6)]) + \
                                  load_images(WHALE_SPRITESHEET, SPRITE_WIDTH, 39,
                                              (self.SCALE * 20, self.SCALE * 8), [(1, 5)])
        self.right_attack_images = invert_images(self.left_attack_images)

        self.img_indexes = {m.id: 0 for m in self.monsters}

    def update(self):
        super(WhaleSprite, self).update()

        for whale in self.monsters:
            if whale.id not in self.attack_count:
                self.attack_count[whale.id] = {'sound': Sound(self.cry_sound_path), 'during_attack': False}
            attack_count = self.attack_count[whale.id]
            if whale.attacking and not attack_count['during_attack']:
                attack_count['sound'].play()
                attack_count['during_attack'] = True
            else:
                attack_count['during_attack'] = False


def load_images(spritesheet, sprite_width, sprite_height, scale, positions):
    return [pygame.transform.scale(
        spritesheet.image_at(
            (a * sprite_width, b * sprite_height, sprite_width, sprite_height), -1
        ).convert_alpha(),
        scale,
    )
        for a, b in positions
    ]


def invert_images(images):
    return [pygame.transform.flip(mi, True, False) for mi in images]
