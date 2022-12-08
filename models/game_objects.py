import random

from models.common import Left, Right, Up, Directions


class Player:
    def __init__(self):
        self.direction = None

    def controls(self, left, right, jump):
        self.control_keys = {left: Left, right: Right, jump: Up}

    def command(self, control):
        if control in self.control_keys.keys():
            cmd = self.control_keys[control]()
            cmd.execute(self)
            return cmd

    def move(self, direction: Directions = None):
        """Add one piece, pop one out."""
        if direction:
            self.direction = direction


class Monster:
    def __init__(self, start_width=0, stop_width=0, start_height=0, stop_height=0):
        self.start_width = start_width
        self.stop_width = stop_width
        self.start_height = start_height
        self.stop_height = stop_height
        self.spawn()

    def spawn(self):
        self.pos = [
            random.randrange(self.start_width, self.stop_width),
            random.randrange(self.start_height, self.stop_height),
        ]
        return self.pos

    def clone(self):
        raise NotImplemented


class BirdLike(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0, stop_height=0):
        super().__init__(start_width, stop_width, start_height, stop_height)

    def clone(self) -> Monster:
        return BirdLike(self.start_width, self.stop_width, self.start_height, self.stop_height)


class SpiderLike(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0, stop_height=0):
        super().__init__(start_width, stop_width, start_height, stop_height)

    def spawn(self):
        self.pos = [
            random.randrange(self.start_width, self.stop_width),
            500,
        ]
        return self.pos

    def clone(self) -> Monster:
        return SpiderLike(self.start_width, self.stop_width, self.start_height, self.stop_height)


class Whale(Monster):
    def __init__(self, start_width=0, stop_width=0, start_height=0, stop_height=0):
        super().__init__(start_width, stop_width, start_height, stop_height)

    def clone(self) -> Monster:
        return Whale(self.start_width, self.stop_width, self.start_height, self.stop_height)


class Spawner:
    def spawn_monster(self, prototype) -> Monster:
        return prototype.clone()
