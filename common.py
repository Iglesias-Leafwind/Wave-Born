from enum import Enum
from datetime import datetime

EVENT_FOOD_EATEN = "event_food_eaten"


class Directions(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __getitem__(self, item):
        return self.value[item]


class Actor:
    def __init__(self):
        self.name = "Unknown"

    def move(self, direction: Directions):
        raise NotImplemented


class Command:
    def __init__(self):
        self.actor = None
        self.dt = datetime.now()

    def execute(self, actor):
        raise NotImplemented

    def __str__(self):
        return f"[{self.dt}] {self.actor.name}: {self.__class__.__name__}"


class Up(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move(Directions.UP)


class Down(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move(Directions.DOWN)


class Left(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move(Directions.LEFT)


class Right(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move(Directions.RIGHT)


class Jump(Command):
    def execute(self, actor):
        self.actor = actor
        actor.move(Directions.UP)


class Subject:
    def __init__(self):
        self.events = {}

    def register(self, event, event_handler):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(event_handler)

    def notify(self, event):
        for event_handler in self.events[event]:
            event_handler(self)