import random
import time

import pygame

from models.fsm import Transition, Move, Attack, Jump, Fall, Dead, Event, Dying, FSM, MoveInAir
from models.player import Player
from models.wave import Wave, Waves
from models.world import World

STATES = [Move, Attack, Jump, Fall, Dead]


class Monster:
    _ID = 0

    USER_POS = None
    USER_WIDTH_OFFSET = 32
    USER_HEIGHT_OFFSET = 32
    TRANSITIONS = {
        Event.ATTACK: [Transition(Move, Attack)],
        Event.MOVE: [Transition(Attack, Move)],
        Event.DEAD: [
            Transition(Move, Dead),
            Transition(Attack, Dead),
        ],
    }
    SPRITE = None

    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1,
                 attack_prob=0.05,
                 cry_prob=0.05):
        self.width = width
        self.height = height
        self.start_width = start_width
        self.stop_width = stop_width
        self.start_height = start_height
        self.stop_height = stop_height
        self.direction = random.choice([-1, 1])
        self.dying = False
        self.is_dead = False
        self.attacking = False
        self.jump_count = 0  # number of UP actions done for a jump
        self.jump_limit = jump_limit  # max number of UP actions per each jump
        self.jumping = False  # is jumping
        self.jump_dist_x = jump_dist_x
        self.jump_dist_y = jump_dist_y
        self.falling = False  # is falling
        self.attack_prob = attack_prob
        self.cry_prob = cry_prob
        self.id = self._get_id()
        self.offset = 1
        self.fsm: FSM
        self.spawn()

    def update(self, **kwargs):
        self.sprite = kwargs['sprite']

    def want_attack(self):
        # verify if the monster wants to attack the player
        return random.random() <= self.attack_prob

    def want_cry(self):
        # verify if the monster wants to cry
        return random.random() <= self.cry_prob

    @classmethod
    def set_user_pos(cls, pos, width_offset=32, height_offset=32):
        cls.USER_POS = pos
        cls.USER_WIDTH_OFFSET = width_offset
        cls.USER_HEIGHT_OFFSET = height_offset

    def _get_id(self):
        id = Monster._ID
        Monster._ID = id + 1
        return id

    def jump(self):
        # reduces monster's y until it reaches the maximum height
        old_pos = self.pos
        if self.jump_count < self.jump_limit:
            self.pos = old_pos[0], old_pos[1] - self.jump_dist_y
            self.jump_count += 1
        else:
            self.jumping = False
            self.falling = True

    def fall(self):
        # increments monster's y until it steps on a block
        old_pos = self.pos
        if self.jump_count > 0:
            self.pos = old_pos[0], old_pos[1] + self.jump_dist_y
            self.jump_count -= 1
        else:
            self.falling = False

    def move(self):
        # updates monster's x according with its direction
        old_pos = self.pos
        self.turn_dirc_if_hit_wall()
        new_pos = old_pos[0] + self.direction, old_pos[1]
        self.pos = new_pos

    def attack(self):
        # changes the flag attacking to True if the monster is not dying or already dead
        if not self.dying and not self.is_dead:
            self.attacking = True

    def dead(self):
        # monster starts dying
        self.dying = True
        self.attacking = False

    def spawn(self):
        # clone method
        if not Monster.USER_POS:
            self.pos = [
                random.randrange(self.stop_width - 16 * 15, self.stop_width),
                random.randrange(self.start_height, self.stop_height),
            ]
            return self.pos

        while True:
            self.pos = [
                random.randrange(self.stop_width - 16 * 8, self.stop_width),
                random.randrange(self.start_height, self.stop_height),
            ]
            if self.x >= Monster.USER_POS[0] + Monster.USER_WIDTH_OFFSET or self.x <= Monster.USER_POS[
                0] - Monster.USER_WIDTH_OFFSET:

                if self.check_inside_walls():
                    continue
                return self.pos

    def out_of_world(self):
        # check if the monster is out of the world
        return self.x < 0 or self.x > self.width or self.y > self.height or self.y < 0

    def turn_dirc_if_hit_wall(self):
        # Invert the monster's direction if it hits a wall

        blocks = World.get_or_create().get_blocks()
        for b in blocks:
            self.sprite.rect.x += self.offset * self.direction
            if pygame.sprite.collide_mask(b, self.sprite):
                self.sprite.rect.x -= self.offset * self.direction
                if not self.attacking and not self.falling:
                    self.direction *= -1
                return True
            self.sprite.rect.x -= self.offset * self.direction

    def check_inside_walls(self):
        # check if the monster is inside of the walls

        blocks = World.get_or_create().get_blocks()
        for b in blocks:
            if abs(self.x - b.rect.x) < 32 and abs(self.y - b.rect.y) < 32:
                return True

    def step_on_wall(self):
        # check if the monster steps on a wall

        blocks = World.get_or_create().get_blocks()
        for b in blocks:
            self.sprite.rect.y += 5
            if pygame.sprite.collide_mask(b, self.sprite):
                self.sprite.rect.x -= 5 * self.direction
                self.sprite.rect.y -= 5
                if pygame.sprite.collide_mask(b, self.sprite):
                    self.sprite.rect.x += 5 * self.direction
                    continue
                self.sprite.rect.x += 5 * self.direction
                return True
            self.sprite.rect.y -= 5

    @classmethod
    def get_sprite(cls):
        return cls.SPRITE

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, v):
        self.pos = v, self.y

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, v):
        self.pos = self.x, v

    def clone(self):
        raise NotImplemented


class Feather:
    # used by BirdLike to attack the player
    _ID = 0

    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction
        self.id = self._next_id()

    def _next_id(self):
        id = Feather._ID
        Feather._ID = id + 1
        return id


class BirdLike(Monster):
    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0, jump_limit=7, jump_dist_x=7,
                 jump_dist_y=1, attack_prob=0.05, cry_prob=0.01):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob, cry_prob)
        self.fsm = FSM(STATES, Monster.TRANSITIONS)

    def dead(self):
        self.is_dead = True

    def update(self, **kwargs):
        super(BirdLike, self).update(**kwargs)

        # update the monster's state
        event = None
        player = Player.SPRITE
        if player.stepped_on(self.sprite.rect) or self.out_of_world():
            event = Event.DEAD
        elif self.fsm.current == Attack:
            event = Event.MOVE
        elif self.fsm.current == Move and self.want_attack():
            event = Event.ATTACK

        self.fsm.update(event, self)

    def clone(self) -> Monster:
        return BirdLike(self.width, self.height, self.start_width, self.stop_width, self.start_height, self.stop_height,
                        self.jump_limit,
                        self.jump_dist_x, self.jump_dist_y, self.attack_prob, self.cry_prob)

    def get_center(self, width, height):
        # the center of the monster will be used as "launch point" of Feather
        if self.direction == 1:
            return self.pos[0] + width // 2, self.pos[1] + height // 2
        return self.pos[0], self.pos[1] + height // 2


class GroundMonster(Monster):
    # class for monsters that walk on the blocks

    TRANSITIONS = {
        Event.ATTACK: [Transition(Move, Attack)],
        Event.JUMP: [Transition(Attack, Jump)],
        Event.FALL: [Transition(Jump, Fall), Transition(MoveInAir, Fall)],
        Event.MOVE: [Transition(Fall, Move)],
        Event.MOVE_IN_AIR: [Transition(Move, MoveInAir)],
        Event.DYING: [
            Transition(Move, Dying),
            Transition(Attack, Dying),
            Transition(Jump, Dying),
            Transition(Fall, Dying),
        ],
        Event.DEAD: [
            Transition(Dying, Dead),
            Transition(Move, Dead),
            Transition(Attack, Dead),
            Transition(Jump, Dead),
            Transition(Fall, Dead), ]
    }

    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0, jump_limit=7, jump_dist_x=7,
                 jump_dist_y=1, attack_prob=0.05, cry_prob=0.05):
        super(GroundMonster, self).__init__(width, height, start_width, stop_width, start_height, stop_height,
                                            jump_limit,
                                            jump_dist_x,
                                            jump_dist_y, attack_prob, cry_prob)
        self.fsm = FSM(STATES, GroundMonster.TRANSITIONS)
        self.fail_speed = 1

    def update(self, **kwargs):
        super(GroundMonster, self).update(**kwargs)
        event = None
        player = Player.SPRITE
        if player.stepped_on(self.sprite.rect):
            event = Event.DYING
        elif self.out_of_world():
            event = Event.DEAD
        elif self.fsm.current == Jump and self.falling:
            event = Event.FALL
        elif self.fsm.current == Fall and not self.falling:
            event = Event.MOVE
            self.fail_speed = 1
        elif self.fsm.current == Attack:
            event = Event.JUMP
        elif self.fsm.current == Move and not self.step_on_wall():
            event = Event.MOVE_IN_AIR
        elif self.fsm.current == Move and \
                abs(player.y - self.y) < 32 and abs(player.x - self.x) < 128 and self.want_attack():
            if not self.attacking:
                if player.rect.x < self.x:
                    self.direction = -1
                else:
                    self.direction = 1
                event = Event.ATTACK
        elif self.fsm.current == MoveInAir:
            event = Event.FALL
            self.fail_speed = 2

        self.fsm.update(event, self)

    def spawn(self):
        self.pos = [super(GroundMonster, self).spawn()[0], self.stop_height]
        offset = 0
        while True:
            if self.check_inside_walls():
                self.pos = [self.pos[0], self.stop_height + offset]
                offset -= 16
                continue
            return self.pos

    def jump(self, **kwargs):
        old_pos = self.pos

        # jump until hits a wall
        if self.jump_count < self.jump_limit:
            if self.turn_dirc_if_hit_wall():
                self.pos = old_pos[0], \
                           old_pos[1] - self.jump_dist_y
            else:
                self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                           old_pos[1] - self.jump_dist_y

            self.jump_count += 1
        else:
            self.start_fail()

    def start_fail(self):
        self.jumping = False
        self.falling = True

    def fall(self, **kwargs):
        old_pos = self.pos

        # fall until hits a wall
        if self.attacking and self.jump_count > 0:
            self._fail(old_pos)
            self.jump_count -= 1
        elif not self.step_on_wall():
            self.attacking = False
            self._fail(old_pos)
        else:
            self.stop_fail()

    def _fail(self, old_pos):
        if self.turn_dirc_if_hit_wall():
            self.pos = old_pos[0], \
                       old_pos[1] + self.jump_dist_y * self.fail_speed
        else:
            self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                       old_pos[1] + self.jump_dist_y * self.fail_speed

    def stop_fail(self):
        self.jump_count = 0
        self.falling = False

    def attack(self):
        super(GroundMonster, self).attack()
        self.jumping = True
        self.falling = False
        self.jump_count = 0
        self.get_sprite().change_monster_state(self)


class SpiderLike(GroundMonster):
    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1,
                 attack_prob=0.005):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob=attack_prob)

        self.offset = 3

    def clone(self) -> Monster:
        return SpiderLike(self.width, self.height, self.start_width, self.stop_width, self.start_height,
                          self.stop_height, self.jump_limit,
                          self.jump_dist_x, self.jump_dist_y, self.attack_prob)

    SPRITE = None

class TurtleLike(GroundMonster):
    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=3,
                 jump_dist_x=7,
                 jump_dist_y=1, attack_prob=0.005, cry_prob=0.02):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob, cry_prob)
        self.offset = 2

    def clone(self) -> Monster:
        return TurtleLike(self.width, self.height, self.start_width, self.stop_width, self.start_height,
                          self.stop_height, self.jump_limit,
                          self.jump_dist_x, self.jump_dist_y, self.attack_prob, self.cry_prob)
    SPRITE = None


class Whale(Monster):
    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 attack_interval=5,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1, attack_prob=0.05):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob)
        self.attack_interval = attack_interval
        self.direction = -1
        self.fsm = FSM(STATES, Monster.TRANSITIONS)
        self.attack_info = {'time': 1 << 31,
                            'finished': 0,
                            'wave': None,
                            'wait': random.randint(1, self.attack_interval)}

    def out_of_world(self):
        return self.x < -100 or self.x > self.width or self.y > self.height or self.y < 0

    def attack(self):
        if not self.attacking:
            whale_attack = self.attack_info
            super(Whale, self).attack()
            if whale_attack['finished'] == 0 or time.time() - whale_attack['finished'] >= whale_attack['wait']:
                whale_attack['time'] = time.time()
                wave = Wave([self.x + (self.x / 4), 3.5 * self.y], 1, 144,
                            [0, whale_attack['wait'] / 2])
                Waves.get_or_create().add_wave(wave)
        Whale.SPRITE.change_monster_state(self)

    def update(self, **kwargs):
        super(Whale, self).update(**kwargs)
        event = None
        if self.out_of_world():
            event = Event.DEAD
        elif self.fsm.current == Attack and time.time() - self.attack_info['time'] >= self.attack_interval:
            event = Event.MOVE
            self.attacking = False
            Whale.SPRITE.change_monster_state(self)
        elif self.fsm.current == Move and self.want_attack():
            event = Event.ATTACK
            self.attack_info['time'] = time.time()

        self.fsm.update(event, self)

    def dead(self):
        self.is_dead = True

    def spawn(self):
        self.pos = [
            self.stop_width // 2,
            50
        ]
        return self.pos

    def clone(self) -> Monster:
        return Whale(self.width, self.height, self.start_width, self.stop_width, self.start_height,
                     self.stop_height,
                     self.attack_interval,
                     self.jump_limit,
                     self.jump_dist_x,
                     self.jump_dist_y, self.attack_prob)

    SPRITE = None

class Spawner:
    def spawn_monster(self, prototype) -> Monster:
        return prototype.clone()
