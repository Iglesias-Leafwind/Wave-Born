import logging

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
