from models.common import Directions, Left, Right, Up


class Player:
    SPRITE = None

    def __init__(self, x, y):
        self.direction = None
        self.dead = False
        self.won = False
        self.pos = (x, y)

    def controls(self, left, right, jump):
        # store control keys
        self.control_keys = {left: Left, right: Right, jump: Up}
        self.control_keys_name = {'left': left, 'right': right, 'jump': jump}

    def command(self, control):
        # move the player according with the control
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
