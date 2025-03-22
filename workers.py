import random
from constants import EMPTY, ASSEMBLY_DURATION, FINISHED


class Worker:

    UP: str = '^'
    DOWN: str = 'v'

    def __init__(self, index: int, pos: str, slots: list[str]):
        self.index = index
        self.pos = pos
        self.slots = slots
        self.left_hand: str = EMPTY
        self.right_hand: str = EMPTY
        self.assembling: bool = False
        self.assembly_remaining: int = 0
        assert 0 <= index < len(slots)
        assert pos in (self.UP, self.DOWN)

    def __str__(self):
        hands: str = '' if self.left_hand == EMPTY and self.right_hand == EMPTY else f" [{self.left_hand}|{self.right_hand}]"
        asm: str = '' if not self.assembling else f' ({self.assembly_remaining})'
        return f'{self.index}{self.pos}{hands}'

    def work(self) -> bool:
        try:
            if self._get_left():
                return True
            if self._get_right():
                if self._assemble():
                    self.assembly_remaining += 1
                return True
            return False
        finally:
            if self.assembly_remaining > 0:
                self.assembly_remaining -= 1

    def _get_left(self) -> bool:
        if self.left_hand == EMPTY:
            self.left_hand = self.slots[self.index]
            self.slots[self.index] = EMPTY
            return True
        return False

    def _get_right(self) -> bool:
        if self.right_hand == EMPTY:
            self.right_hand = self.slots[self.index]
            self.slots[self.index] = EMPTY
            return True
        return False

    def _assemble(self) -> bool:
        if self.assembling:
            self.assembly_remaining -= 1
            if self.assembly_remaining == 0:
                self.slots[self.index] = FINISHED
                self.left_hand = self.right_hand = EMPTY
                self.assembling = False
            return False
        if self.left_hand == self.right_hand:
            self.assembling = True
            self.assembly_remaining = ASSEMBLY_DURATION
            return True
        return False





class WorkerPair:
    def __init__(self, index: int, slots: list[str]):
        self.up = Worker(index, Worker.UP, slots)
        self.down = Worker(index, Worker.DOWN, slots)

    def work(self):
        workers: list[Worker] = [self.up, self.down] if random.choice([True, False]) else [self.down, self.up]
        for worker in workers:
            if worker.work():
                break