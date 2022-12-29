import random
import time

import pygame

from models.fsm import Transition, Move, Attack, Jump, Fail, Dead, Event, Dying, FSM, MoveInAir
from models.player import Player
from models.wave import Wave, Waves
from models.world import World

STATES = [Move, Attack, Jump, Fail, Dead]


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
        self.right_offset = 64
        self.left_offset = 64
        self.fsm: FSM
        self.spawn()

    def update(self, **kwargs):
        self.sprite = kwargs['sprite']

    def want_attack(self):
        return random.random() <= self.attack_prob

    def want_cry(self):
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
        old_pos = self.pos
        if self.jump_count < self.jump_limit:
            self.pos = old_pos[0], old_pos[1] - self.jump_dist_y
            self.jump_count += 1
        else:
            self.jumping = False
            self.falling = True

    def fail(self):
        old_pos = self.pos
        if self.jump_count > 0:
            self.pos = old_pos[0], old_pos[1] + self.jump_dist_y
            self.jump_count -= 1
        else:
            self.falling = False

    def move(self):
        old_pos = self.pos
        self.turn_dirc_if_hit_wall()
        new_pos = old_pos[0] + self.direction, old_pos[1]
        self.pos = new_pos

    def attack(self):
        if not self.dying and not self.is_dead:
            self.attacking = True

    def dead(self):
        self.dying = True
        self.attacking = False

    def spawn(self):
        if not Monster.USER_POS:
            self.pos = [
                random.randrange(self.start_width, self.stop_width),
                random.randrange(self.start_height, self.stop_height),
            ]
            return self.pos

        while True:
            self.pos = [
                random.randrange(self.start_width, self.stop_width),
                random.randrange(self.start_height, self.stop_height),
            ]
            if self.x >= Monster.USER_POS[0] + Monster.USER_WIDTH_OFFSET or self.x <= Monster.USER_POS[
                0] - Monster.USER_WIDTH_OFFSET \
                    or self.y <= Monster.USER_POS[1] + Monster.USER_HEIGHT_OFFSET or self.y >= Monster.USER_POS[
                1] - Monster.USER_HEIGHT_OFFSET:

                if self.check_inside_walls():
                    continue
                return self.pos

    def out_of_world(self):
        return self.x < 0 or self.x > self.width or self.y > self.height or self.y < 0

    def turn_dirc_if_hit_wall(self):
        blocks = World.get_or_create().get_blocks()
        for b in blocks:

            if self.direction == 1:
                if pygame.sprite.collide_mask(b, self.sprite):
                    if not self.attacking:
                        self.direction = -1
                        self.x -= 32
                    return True
            elif self.direction == -1:
                if pygame.sprite.collide_mask(b, self.sprite):
                    if not self.attacking:
                        self.direction = 1
                        self.x += 32
                    return True

    def check_inside_walls(self):
        blocks = World.get_or_create().get_blocks()
        for b in blocks:
            if abs(self.x - b.rect.x) < 32 and abs(self.y - b.rect.y) < 32:
                return True

    def step_on_wall(self):
        blocks = World.get_or_create().get_blocks()
        for b in blocks:
            if pygame.sprite.collide_mask(b, self.sprite):
                return True

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
        if self.direction == 1:
            return self.pos[0] + width // 2, self.pos[1] + height // 2
        return self.pos[0], self.pos[1] + height // 2


class GroundMonster(Monster):
    TRANSITIONS = {
        Event.ATTACK: [Transition(Move, Attack)],
        Event.JUMP: [Transition(Attack, Jump)],
        Event.FAIL: [Transition(Jump, Fail), Transition(MoveInAir, Fail)],
        Event.MOVE: [Transition(Fail, Move)],
        Event.MOVE_IN_AIR: [Transition(Move, MoveInAir)],
        Event.DYING: [
            Transition(Move, Dying),
            Transition(Attack, Dying),
            Transition(Jump, Dying),
            Transition(Fail, Dying),
        ],
        Event.DEAD: [
            Transition(Dying, Dead),
            Transition(Move, Dead),
            Transition(Attack, Dead),
            Transition(Jump, Dead),
            Transition(Fail, Dead), ]
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
            event = Event.FAIL
        elif self.fsm.current == Fail and not self.falling:
            event = Event.MOVE
            self.fail_speed = 1
        elif self.fsm.current == Attack:
            event = Event.JUMP
        elif self.fsm.current == Move and \
                abs(player.y - self.y) < 32 and abs(player.x - self.x) < 128 and self.want_attack():
            if not self.attacking:
                if player.rect.x < self.x:
                    self.direction = -1
                else:
                    self.direction = 1
                event = Event.ATTACK
        elif self.fsm.current == Move:
            if not self.step_on_wall():
                event = Event.MOVE_IN_AIR
        elif self.fsm.current == MoveInAir:
            event = Event.FAIL
            self.fail_speed = 2

        self.fsm.update(event, self)

    def spawn(self):
        while True:
            self.pos = [
                random.randrange(self.start_width, self.stop_width),
                self.stop_height,
            ]
            if self.check_inside_walls():
                continue
            return self.pos

    def jump(self, **kwargs):
        old_pos = self.pos
        if self.jump_count < self.jump_limit:
            if self.turn_dirc_if_hit_wall():
                self.pos = old_pos[0], \
                           old_pos[1] - self.jump_dist_y
                print(f"{self.id} {self.pos}")
            else:
                self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                           old_pos[1] - self.jump_dist_y

            self.jump_count += 1
        else:
            self.start_fail()

    def start_fail(self):
        self.jumping = False
        self.falling = True

    def fail(self, **kwargs):
        old_pos = self.pos
        if self.attacking and self.jump_count > 0:
            self._fail(old_pos)
            self.jump_count -= 1
        elif not self.step_on_wall():
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
    SPRITE = None

    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1,
                 attack_prob=0.005):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob=attack_prob)

        self.right_offset = 64
        self.left_offset = 50

    def clone(self) -> Monster:
        return SpiderLike(self.width, self.height, self.start_width, self.stop_width, self.start_height,
                          self.stop_height, self.jump_limit,
                          self.jump_dist_x, self.jump_dist_y, self.attack_prob)


class TurtleLike(GroundMonster):
    SPRITE = None

    def __init__(self, width, height, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=3,
                 jump_dist_x=7,
                 jump_dist_y=1, attack_prob=0.005, cry_prob=0.02):
        super().__init__(width, height, start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x,
                         jump_dist_y,
                         attack_prob, cry_prob)
        self.right_offset = 110
        self.left_offset = 50

    def clone(self) -> Monster:
        return TurtleLike(self.width, self.height, self.start_width, self.stop_width, self.start_height,
                          self.stop_height, self.jump_limit,
                          self.jump_dist_x, self.jump_dist_y, self.attack_prob, self.cry_prob)


class Whale(Monster):
    SPRITE = None

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
        return Whale(self.width, self.height, start_width=0, stop_width=0, start_height=0,
                     stop_height=0,
                     attack_interval=5,
                     jump_limit=7,
                     jump_dist_x=7,
                     jump_dist_y=1, attack_prob=0.01)


class Spawner:
    def spawn_monster(self, prototype) -> Monster:
        return prototype.clone()
