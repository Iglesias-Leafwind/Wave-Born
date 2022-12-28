import random
import time
from enum import Enum

import pygame

from models.common import Left, Right, Up, Directions
from models.fsm import State, Transition, FSM


class Event(Enum):
    MOVE = 1,
    ATTACK = 2,
    JUMP = 3,
    FAIL = 4,
    DYING = 5,
    DEAD = 6


class Move(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.move()

    @classmethod
    def enter(cls, monster):
        monster.attacking = False


class Attack(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def enter(cls, monster):
        monster.attack()
        if not isinstance(monster, BirdLike):
            monster.SPRITE.change_monster_state(monster)


class Jump(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.jump()


class Fail(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.fail()


class Dying(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def enter(cls, monster):
        monster.dead()


class Dead(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.is_dead = True


STATES = [Move, Attack, Jump, Fail, Dead]


class Player:
    SPRITE = None

    def __init__(self, x, y):
        self.direction = None
        self.dead = False
        self.pos = (x, y)

    def controls(self, left, right, jump):
        self.control_keys = {left: Left, right: Right, jump: Up}
        self.control_keys_name = {'left': left, 'right': right, 'jump': jump}

    def command(self, control):
        if control in self.control_keys.keys():
            cmd = self.control_keys[control]()
            cmd.execute(self)
            return cmd

    def move(self, direction: Directions = None):
        """Add one piece, pop one out."""
        if direction:
            self.direction = direction

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

    @property
    def left_key(self):
        return self.control_keys_name['left']

    @property
    def right_key(self):
        return self.control_keys_name['right']

    @property
    def jump_key(self):
        return self.control_keys_name['jump']


class Wave:
    def __init__(self, center, velocity, clockticks, sound_interval):
        # sound_interval = (sound_start,sound_end)
        clockticks = 3 * clockticks / 4
        self.radius = -velocity * clockticks * sound_interval[0] if sound_interval[0] > 0 else 0
        self.x = center[0]
        self.y = center[1]
        self.thicc = int(clockticks * (sound_interval[1] - sound_interval[0]))
        self.velocity = velocity
        self.sound_interval = sound_interval

    def update(self):
        self.radius += self.velocity

    def draw(self, mask):
        pygame.draw.circle(mask, (0, 0, 255), (self.x, self.y), self.radius, self.thicc)

    def checkLimits(self, WIDTH, HEIGHT):
        limits = [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]
        return all((abs(limit[0] - self.x) + abs(limit[1] - self.y)) < self.radius for limit in limits)


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
        self.spawn()

    def update(self, **kwargs):
        pass

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
                return self.pos

    def out_of_world(self):
        return self.x < 0 or self.x > self.width or self.y > self.height or self.y < 0

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
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction


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

    def update(self, player_pos):
        event = None
        player = Player.SPRITE
        if player.stepped_on(self.x, self.y) or self.out_of_world():
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
        Event.FAIL: [Transition(Jump, Fail)],
        Event.MOVE: [Transition(Fail, Move)],
        Event.DYING: [
            Transition(Move, Dead),
            Transition(Attack, Dead),
            Transition(Jump, Dead),
            Transition(Fail, Dead),
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

    def update(self, player_pos):
        event = None
        player = Player.SPRITE
        if player.stepped_on(self.x, self.y):
            event = Event.DYING
        elif self.out_of_world():
            event = Event.DEAD
        elif self.fsm.current == Jump and self.falling:
            event = Event.FAIL
        elif self.fsm.current == Fail and not self.falling:
            event = Event.MOVE
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

        self.fsm.update(event, self)

    def spawn(self):
        self.pos = [
            random.randrange(self.start_width, self.stop_width),
            self.stop_height,
        ]
        return self.pos

    def jump(self):
        old_pos = self.pos
        if self.jump_count < self.jump_limit:
            self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                       old_pos[1] - self.jump_dist_y
            self.jump_count += 1
        else:
            self.jumping = False
            self.falling = True

    def fail(self):
        old_pos = self.pos
        if self.jump_count >= 0:
            self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                       old_pos[1] + self.jump_dist_y
            self.jump_count -= 1
        else:
            self.jump_count = 0
            self.falling = False

    def attack(self):
        super(GroundMonster, self).attack()
        self.jumping = True
        self.falling = False
        self.jump_count = 0


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

    def update(self, player_pos):
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


class Waves:
    _singleton = None

    def __init__(self, waves=None):
        if waves is None:
            waves = []
        self.waves = waves
        self._i = 0
        Waves._singleton = self

    def add_wave(self, wave):
        self.waves.append(wave)

    def remove(self, wave):
        self.waves.remove(wave)

    @staticmethod
    def get_or_create(**kwargs):
        if Waves._singleton:
            return Waves._singleton
        return Waves(**kwargs)

    def __iter__(self):
        return self

    def __next__(self):
        if self._i < len(self.waves):
            i = self._i
            self._i += 1
            return self.waves[i]
        self._i = 0
        raise StopIteration()


class Spawner:
    def spawn_monster(self, prototype) -> Monster:
        return prototype.clone()
