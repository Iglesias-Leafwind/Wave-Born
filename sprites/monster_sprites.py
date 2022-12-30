import random
import time

import pygame
from pygame.sprite import Sprite

from models.monsters import Feather, SpiderLike, TurtleLike
from models.sound import Sound
from models.wave import Wave, Waves
from sprites.player_sprite import PlayerSprite
from sprites.spritesheet import SpriteSheet

from sprites.utils import load_images, invert_images


class MonsterSprite(pygame.sprite.Sprite):
    _singleton = None

    def __init__(self, image_update_per_frames=0, pos_update_per_frames=0):
        Sprite.__init__(self)
        self.monsters: list
        self.rects: dict
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
        if cls._singleton:
            return cls._singleton
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

    def _add_monster(self, monster):
        self.monsters.append(monster)
        id = monster.id
        self.img_indexes[id] = 0

    def update(self, **kwargs):
        if self.pos_update_count >= self.pos_update_per_frames:
            for monster in self.monsters:
                self.image, self.rect = self.rects[monster.id]
                if not monster.dying:
                    monster.update(**kwargs, sprite=self)

            self.pos_update_count = 0
        else:
            self.pos_update_count += 1

    def draw(self, mask):
        self.image_update_count += 1
        for monster in self.monsters:
            image = self._next_image(monster)
            mask.blit(
                image,
                (monster.x, monster.y),
            )
            rect = image.get_rect()
            rect.x = monster.x
            rect.y = monster.y
            self.rects[monster.id] = (image, rect)
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
        self.rects = {f.id: self.rect for f in self.feathers}
        FeatherSprite.__feather_sprite = self

    @staticmethod
    def get_or_create(**kwargs):
        if FeatherSprite.__feather_sprite:
            return FeatherSprite.__feather_sprite
        else:
            return FeatherSprite(**kwargs)

    def add_feather(self, bird_id, feather):
        self.feathers[bird_id] = feather
        self.rects[feather.id] = self.rect

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

    def _has_collision_or_out_of_world(self, feather, WIDTH, HEIGHT):
        player = PlayerSprite.get_or_create()
        if player.has_collision_with(self.rects[feather.id]):
            player.dead()
            return True
        if feather.pos[0] < 0 or feather.pos[0] > WIDTH or feather.pos[1] > HEIGHT:
            return True

    def update(self):
        to_be_removed = []
        for bird_id, feather in self.feathers.items():
            old_pos = feather.pos
            new_pos = old_pos[0] + feather.direction, old_pos[1] + 1
            if self._has_collision_or_out_of_world(feather, self.WIDTH, self.HEIGHT):
                to_be_removed.append(bird_id)
            else:
                feather.pos = new_pos
                rect = self.image.get_rect()
                rect.x = feather.pos[0]
                rect.y = feather.pos[1]
                self.rects[feather.id] = rect

        for i in to_be_removed:
            del self.rects[self.feathers[i].id]
            del self.feathers[i]

    def update_camera_movement(self, movement):
        for bird_id, feather in self.feathers.items():
            old_pos = feather.pos
            feather.pos = old_pos[0] - movement, old_pos[1]


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
        self.image = pygame.Surface(self.left_move_images[0].get_size())
        self.rect = self.image.get_rect()
        self.rects = {m.id: (self.image, self.image.get_rect()) for m in self.monsters}
        self.mask = pygame.mask.from_surface(self.image)
        BirdLikeSprite._singleton = self

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

    def _add_monster(self, bird):
        super(BirdLikeSprite,self)._add_monster(bird)
        id = bird.id
        self.rects[id] = (self.image, self.image.get_rect())
        self.img_indexes[id] = 0

    def update(self, **kwargs):
        super(BirdLikeSprite, self).update(**kwargs)

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

    def update_camera_movement(self, movement):
        for bird in self.monsters:
            bird.x = bird.x - movement
        self.feather_sprite.update_camera_movement(movement)


class GroundMonsterSprite(MonsterSprite):
    def update(self, **kwargs):
        super(GroundMonsterSprite, self).update(**kwargs)
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

        self.monsters = spiders
        self.cry_interval = 10
        self.cry_count = {}
        self.SCALE = SCALE
        self.width = WIDTH
        self.height = HEIGHT
        self._init_images()
        self.image = pygame.Surface(self.left_move_images[0].get_size())
        self.rect = self.image.get_rect()
        
        self.rects = {m.id: (self.image, self.image.get_rect()) for m in self.monsters}
        self.mask = pygame.mask.from_surface(self.image)
        SpiderLikeSprite._singleton = self

    def _init_images(self):
        SPIDER_SPRITESHEET = SpriteSheet("sources/imgs/spider.png")
        self.sprite_width = 128
        self.sprite_height = 124

        self.left_move_images = [(i, 0) for i in range(12)]
        self.left_move_images = load_images(SPIDER_SPRITESHEET, self.sprite_width, self.sprite_height,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            self.left_move_images)

        self.left_dead_images = [(i, 0) for i in range(16, 23)]
        self.left_dead_images = load_images(SPIDER_SPRITESHEET, self.sprite_width, self.sprite_height,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            self.left_dead_images)

        self.right_move_images = invert_images(self.left_move_images)
        self.right_dead_images = invert_images(self.left_dead_images)

        self.left_attack_images = load_images(SPIDER_SPRITESHEET, self.sprite_width, self.sprite_height,
                                              (self.SCALE * 2, self.SCALE * 2),
                                              [(i, 0) for i in range(12, 17)])

        self.right_attack_images = invert_images(self.left_attack_images)

        self.img_indexes = {m.id: 0 for m in self.monsters}

    def update(self, **kwargs):
        super(SpiderLikeSprite, self).update(**kwargs)
        for spider in self.monsters:
            if spider.is_dead:
                self._remove_monster(spider)

    def _add_monster(self, spider):
        super(SpiderLikeSprite,self)._add_monster(spider)
        id = spider.id
        self.rects[id] = (self.image, self.image.get_rect())
        self.img_indexes[id] = 0

    def update_camera_movement(self, movement):
        for spider in self.monsters:
            spider.x -= movement


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
        self.image = pygame.Surface(self.left_move_images[0].get_size())
        self.rect = self.image.get_rect()
        self.rects = {m.id: (self.image, self.image.get_rect()) for m in self.monsters}
        self.mask = pygame.mask.from_surface(self.image)
        TurtleLikeSprite._singleton = self

    def _init_images(self):
        TURTLE_SPRITESHEET = SpriteSheet("sources/imgs/tortoise.png")
        self.sprite_width = 33
        self.sprite_height = 42

        self.left_move_images = load_images(TURTLE_SPRITESHEET, self.sprite_width, self.sprite_height,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            [(i, 0) for i in range(3)])

        self.left_dead_images = load_images(TURTLE_SPRITESHEET, 35, 42,
                                            (self.SCALE * 2, self.SCALE * 2),
                                            [(i, 3) for i in range(4)])

        self.right_move_images = invert_images(self.left_move_images)
        self.right_dead_images = invert_images(self.left_dead_images)

        self.left_attack_images = load_images(TURTLE_SPRITESHEET, self.sprite_width, self.sprite_height,
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
            
    def _add_monster(self, turtle):
        super(TurtleLikeSprite,self)._add_monster(turtle)
        id = turtle.id
        self.rects[id] = (self.image, self.image.get_rect())
        self.img_indexes[id] = 0
        
    def update(self, **kwargs):
        super(TurtleLikeSprite, self).update(**kwargs)
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

            #if turtle.dying or turtle.attacking:
            #    self.sound_count[turtle.id]['step'].stop()
            #else:
            #    self.sound_count[turtle.id]['step'].play(loops=-1)

        
    def update_camera_movement(self, movement):
        for turtle in self.monsters:
            turtle.x -= movement


class WhaleSprite(MonsterSprite):
    def __init__(self, whales, SCALE):
        MonsterSprite.__init__(self, 100, 128)
        self.monsters = whales
        self.attack_count = {}
        self.attack_interval = 5  # 10s
        self.cry_sound_path = "sources/sounds/whale.mp3"
        self.SCALE = SCALE
        self._init_images()
        self.image = pygame.Surface(self.left_move_images[0].get_size())
        self.rect = self.image.get_rect()
        self.rects = {m.id: (self.image, self.image.get_rect()) for m in self.monsters}
        self.mask = pygame.mask.from_surface(self.image)
        WhaleSprite._singleton = self

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

    def update(self, **kwargs):
        super(WhaleSprite, self).update(**kwargs)

        for whale in self.monsters:
            if whale.is_dead:
                self._remove_monster(whale)
                continue

            attack_count = self.attack_count[whale.id]
            if whale.attacking and not attack_count['during_attack']:
                attack_count['sound'].play()
                attack_count['during_attack'] = True
            elif not whale.attacking:
                attack_count['during_attack'] = False


    def _add_monster(self, whale):
        super(WhaleSprite,self)._add_monster(whale)
        id = whale.id
        self.rects[id] = (self.image, self.image.get_rect())
        self.img_indexes[id] = 0
        self.attack_count[id] = {'sound': Sound(self.cry_sound_path), 'during_attack': False}
        
    def update_camera_movement(self, movement):
        for whale in self.monsters:
            whale.x -= movement
