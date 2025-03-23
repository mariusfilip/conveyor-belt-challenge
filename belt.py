import random

from constants import EMPTY, COMPONENTS
from workers import Worker, WorkerPair


class Belt:
    """
    A conveyor belt that carries components to be assembled.

    It contains a list of slots that can hold components and finished products and a list of worker pairs that can assemble components.
    """
    _CHOICES: str = COMPONENTS + EMPTY

    def __init__(self, size: int):
        self.slots: list[str] = [Worker.EMPTY] * size
        self.pairs: list[WorkerPair] = [WorkerPair(i, self.slots) for i in range(size)]

    def _tick(self) -> (str, bool):
        """
        Make the belt tick.
        :return: a tuple of the component that was in the last slot and whether the belt changed.
        """
        result: str = self._shift()
        shuffled: list[str] = random.sample(self.pairs, len(self.pairs))
        changed: bool = False
        for pair in shuffled:
            changed = pair.work() or changed
        return result, changed

    def _shift(self, refill: bool = True) -> str:
        """
        Shift the belt by one slot.
        :param refill: True whether to refill the first slot with a random component, False if filling it with an empty slot.
        :return: the component that was in the last slot.
        """
        result: str = self.slots[-1]
        self.slots = [EMPTY] + self.slots[:-1]
        if refill:
            self.slots[0] = random.choice(self._CHOICES)
        return result
