import logging
from enum import Enum


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class State:
    def __init__(self, name) -> None:
        self.name = name

    @classmethod
    def enter(cls, object):
        logging.debug(f"{object} Entering {cls.__name__}")

    @classmethod
    def update(cls, object):
        pass

    @classmethod
    def exit(cls, object):
        pass


class Transition:
    def __init__(self, _from, _to) -> None:
        self._from = _from
        self._to = _to


class FSM:
    def __init__(self, states: list[State], transitions: dict[State, list[Transition]]) -> None:
        self._states = states
        self._transitions = transitions

        self.current: State = self._states[0]
        self.end: State = self._states[-1]

    def update(self, event, object):
        if event:
            for trans in self._transitions.get(event):
                if trans._from == self.current:
                    self.current.exit(object)
                    self.current = trans._to
                    self.current.enter(object)
        self.current.update(object)

        if self.current == self.end:
            self.current.exit(object)
            return False
        return True



class Event(Enum):
    MOVE = 1,
    MOVE_IN_AIR = 2,
    ATTACK = 3,
    JUMP = 4,
    FALL = 5,
    DYING = 6,
    DEAD = 7


class Move(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.move()

    @classmethod
    def enter(cls, monster):
        monster.attacking = False

class MoveInAir(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    @classmethod
    def enter(cls, monster):
        monster.start_fail()

class Attack(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def enter(cls, monster):
        monster.attack()


class Jump(State):
    def __init__(self):
        super().__init__(self.__class__.__name__)

    @classmethod
    def update(cls, monster):
        monster.jump()


class Fall(State):
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
