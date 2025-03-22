import random
from workers import Worker, WorkerPair


class Belt:
    _CHOICES: str = Worker.COMPONENTS + Worker.EMPTY

    def __init__(self, size: int):
        self.slots: list[str] = [Worker.EMPTY] * size
        self.pairs: list[WorkerPair] = [WorkerPair(i, self.slots) for i in range(size)]

    def _tick(self) -> str:
        result: str = self._shift()
        for pair in self.pairs:
            pair.work()
        return result

    def _shift(self) -> str:
        result: str = self.slots[-1]
        self.slots = [None] + self.slots[:-1]
        self.slots[0] = random.choice(self._CHOICES)
        return result
