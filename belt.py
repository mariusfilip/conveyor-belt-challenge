import random

from constants import EMPTY, COMPONENTS, FINISHED
from workers import Worker, WorkerPair


class Belt:
    """
    A conveyor belt that carries components to be assembled.

    It contains a list of slots that can hold components and finished products and a list of worker pairs that can assemble components.
    """
    _CHOICES: str = COMPONENTS + EMPTY

    def __init__(self, size: int, pretty_print: bool = False):
        self.slots: list[str] = [Worker.EMPTY] * size
        self.pairs: list[WorkerPair] = [WorkerPair(i, self.slots) for i in range(size)]
        self.pretty_print: bool = pretty_print

    def pre_fill(self):
        """
        Fill the belt with random components, initially.
        """
        for _ in range(len(self.slots)):
            self._shift(refill=True)

    def work(self, ticks: int) -> (dict[str, int], int):
        """
        Make the belt work for a number of ticks.
        :param ticks: how many ticks to work.
        :return: number of components and finished products produced and how many times the belt changed.
        """
        result: dict[str, int] = {}
        for c in COMPONENTS + [FINISHED]:
            result[c] = 0
        changes: int = 0
        self._print(0)
        for i in range(ticks):
            component, changed = self._tick()
            result[component] += 1
            if changed:
                changes += 1
            self._print(i+1)
        return result, changes

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

    def _print(self, tick: int):
        if self.pretty_print:
            char_matrix: list[list[str]] = self._get_char_matrix()
            lines: list[str] = [Worker.SEP.join(row) for row in char_matrix]
            if tick > 0:
                print(f'Tick {tick}:')
            else:
                print('Initial state:')
            for line in lines:
                print(line)
