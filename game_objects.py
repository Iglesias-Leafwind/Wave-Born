import random

from common import Left, Right, Up, Directions


class Player:
    def __init__(self, leftX=150, leftY=50, width=500, height=500):
        self.leftX = leftX
        self.leftY = leftY
        self.width = width
        self.height = height
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
