import random

import pygame

from models.common import Left, Right, Up, Directions


class Player:
    def __init__(self):
        self.direction = None

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

    def __init__(self, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1):
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
        self.id = self._get_id()
        self.spawn()

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
        self.pos = [
            random.randrange(self.start_width, self.stop_width),
            random.randrange(self.start_height, self.stop_height),
        ]
        return self.pos

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def clone(self):
        raise NotImplemented


class Feather:
    def __init__(self, pos, direction):
        self.pos = pos
        self.direction = direction


class BirdLike(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1):
        super().__init__(start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x, jump_dist_y)

    def clone(self) -> Monster:
        return BirdLike(self.start_width, self.stop_width, self.start_height, self.stop_height)

    def get_center(self, width, height):
        if self.direction == 1:
            return self.pos[0] + width // 2, self.pos[1] + height // 2
        return self.pos[0], self.pos[1] + height // 2


class SpiderLike(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1):
        super().__init__(start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x, jump_dist_y)

    def spawn(self):
        self.pos = [
            random.randrange(self.start_width, self.stop_width),
            500,
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
        if self.jump_count > 0:
            self.pos = old_pos[0] + self.jump_dist_x * self.direction, \
                       old_pos[1] + self.jump_dist_y
            self.jump_count -= 1
        else:
            self.falling = False

    def attack(self):
        super(SpiderLike, self).attack()
        self.jumping = True
        self.falling = False
        self.jump_count = 0

    def clone(self) -> Monster:
        return SpiderLike(self.start_width, self.stop_width, self.start_height, self.stop_height)


class Whale(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0,
                 stop_height=0,
                 jump_limit=7,
                 jump_dist_x=7,
                 jump_dist_y=1):
        super().__init__(start_width, stop_width, start_height, stop_height, jump_limit, jump_dist_x, jump_dist_y)
        self.direction = -1

    def spawn(self):
        self.pos = [
            self.stop_width // 2,
            50
        ]
        return self.pos

    def clone(self) -> Monster:
        return Whale(self.start_width, self.stop_width, self.start_height, self.stop_height)


class Spawner:
    def spawn_monster(self, prototype) -> Monster:
        return prototype.clone()
