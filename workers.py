import logging
import random
from enum import Enum

from constants import EMPTY, ASSEMBLY_DURATION, FINISHED


_logger = logging.getLogger(__name__)

class Worker:
    """
    A worker that can pick up components from the assembly line and assemble them into a finished product.
    """

    # Constants for the worker's position.
    UP: str = '^'
    DOWN: str = 'v'
    SEP: str = '|'

    class State(Enum):
        """
        The possible states of a worker.
        """
        #
        # The worker is ready to start working.
        #
        READY: int = 0
        #
        # The worker has picked up a component with the left hand and it is waiting for the other component for the right hand.
        #
        LEFT_FULL: int = READY + 1
        #
        # The worker has picked up a component with the right hand and is ready to start assembling
        #
        START_ASSEMBLING: int = LEFT_FULL + 1
        #
        # The worker is assembling the components into the finite product.
        #
        ASSEMBLING: int = START_ASSEMBLING + 1
        #
        # The worker has finished assembling the product and is ready to put it back on the assembly line.
        #
        ASSEMBLED: int = ASSEMBLING + 1
        #
        # The worker is holding the finished product in the right hand and is waiting for picking up a new component with the left hand.
        #
        LEFT_EMPTY_RIGHT_FINISHED: int = ASSEMBLED + 1
        #
        # The worker has both hands full: a component in the left hand and the finished product in the right hand.
        #
        LEFT_FULL_RIGHT_FINISHED: int = LEFT_EMPTY_RIGHT_FINISHED + 1

    def __init__(self, index: int, pos: str, slots: list[str]):
        self.index = index
        self.pos = pos
        self.slots = slots
        self.left_hand: str = EMPTY
        self.right_hand: str = EMPTY
        self.assembly_remaining: int = 0
        self.state = self.State.READY
        assert 0 <= index < len(slots)
        assert pos in (self.UP, self.DOWN)

    def __str__(self):
        hands: str = '' if self.left_hand == EMPTY and self.right_hand == EMPTY else f"{self.SEP}{self.left_hand},{self.right_hand}"
        asm: str = '' if not self.state == Worker.State.ASSEMBLING else f'{self.SEP}{self.assembly_remaining}'
        return f'{self.pos}{self.SEP}{self.index}{hands}{asm}'

    def work(self) -> bool:
        """
        Perform one unit of work.
        :return: True if the worker changed the assembly line, False otherwise.
        """
        result: bool = False
        while True:
            match self.state:
                case self.State.READY:
                    _logger.info(f'Worker ({self}) is ready. Trying to pick up a component with left hand first, then with right hand (if needed). '
                                 f'If both hands full, starting assembling ...')
                    if self._get_left():
                        _logger.debug(f'Worker ({self}) got with left hand')
                        self.state = self.State.LEFT_FULL
                        result = True
                    elif self._get_right():
                        _logger.debug(f'Worker ({self}) got with right hand, starting assembling ...')
                        self.state = self.State.START_ASSEMBLING
                        continue
                    break
                case self.State.LEFT_FULL:
                    _logger.info(f'Worker ({self}) is holding a component with the left hand. Trying to pick up another component with the right hand. '
                                 f'If succeeding, then starting assembling ...')
                    if self._get_right():
                        _logger.debug(f'Worker ({self}) got with right hand, starting assembling ...')
                        self.state = self.State.START_ASSEMBLING
                        continue
                    break
                case self.State.START_ASSEMBLING:
                    _logger.info(f'Worker ({self}) starts assembling which will take {self.assembly_remaining} ticks ...')
                    self.assembly_remaining = ASSEMBLY_DURATION
                    self.state = self.State.ASSEMBLING
                    result = True
                    break
                case self.State.ASSEMBLING:
                    _logger.info(f'Worker ({self}) is assembling. If done assembling, then will try setting the finished product back onto the assembly line ...')
                    self.assembly_remaining -= 1
                    if self.assembly_remaining == 0:
                        _logger.debug(f'Worker ({self}) finished assembling. Trying to set the finished product back on the assembly line ...')
                        if self._set_finished():
                            _logger.debug(f'Worker ({self}) set the finished product back on the assembly line')
                            self.state = self.State.ASSEMBLED
                            continue
                        else:
                            _logger.debug(f'Worker ({self}) failed to set the finished product back on the assembly line. '
                                          f'Will be trying to pick up a new component with the left hand ...')
                            self.left_hand = EMPTY
                            self.right_hand = FINISHED
                            self.state = self.State.LEFT_EMPTY_RIGHT_FINISHED
                    break
                case self.State.ASSEMBLED:
                    _logger.info(f'Worker ({self}) has finished assembling the product. Ready to commence assembling another product.')
                    self.state = self.State.READY
                    result = True
                    break
                case self.State.LEFT_EMPTY_RIGHT_FINISHED:
                    _logger.info(f'Worker ({self}) is holding the finished product in the right hand. Trying to set it back onto the assembly line. '
                                 f'Otherwise, trying to pick up a new component with the left hand ...')
                    if self._set_finished(hold_left=True):
                        _logger.debug(f'Worker ({self}) set the finished product back on the assembly line')
                        self.state = self.State.READY
                    elif self._get_left():
                        _logger.debug(f'Worker ({self}) got with left hand')
                        self.state = self.State.LEFT_FULL_RIGHT_FINISHED
                    else:
                        _logger.debug(f'Worker ({self}) failed to set the finished product back on the assembly line and failed to pick up a new component with the left hand. '
                                      f'Waiting ...')
                        break
                    result = True
                    break
                case self.State.LEFT_FULL_RIGHT_FINISHED:
                    _logger.info(f'Worker ({self}) is holding a component in the left hand and the finished product in the right hand. '
                                 f'Trying to set the finished product back on the assembly line. '
                                 f'If succeeded, then will be ready to pick up a new component with the right hand ...')
                    if self._set_finished(hold_left=True):
                        self.state = self.State.LEFT_FULL
                    else:
                        break
                    result = True
                    break
                case _:
                    assert False, f'Invalid state: {self.state}'
                    break
        return result

    def _get_left(self) -> bool:
        """
        Try to pick up a component with the left hand.
        :return: True if the worker picked up a component, False otherwise.
        """
        if self.left_hand == EMPTY and self.slots[self.index] != EMPTY:
            self.left_hand = self.slots[self.index]
            self.slots[self.index] = EMPTY
            return True
        return False

    def _get_right(self) -> bool:
        """
        Try to pick up a component with the right hand.
        :return: True if the worker picked up a component, False otherwise.
        """
        if self.right_hand == EMPTY and self.slots[self.index] != EMPTY and self.slots[self.index] != self.left_hand:
            self.right_hand = self.slots[self.index]
            self.slots[self.index] = EMPTY
            return True
        return False

    def _set_finished(self, hold_left: bool = False) -> bool:
        """
        Try to set the finished product back onto the assembly line.
        :param hold_left: whether to hold the left hand from getting empty or not.
        :return: True if the worker set the finished product back onto the assembly line, False otherwise.
        """
        if self.slots[self.index] == EMPTY:
            assert not hold_left or self.right_hand == FINISHED # If holding the left hand, then the right hand must be holding the finished product.
            self.slots[self.index] = FINISHED
            self.right_hand = EMPTY
            if hold_left:
                pass
            else:
                self.left_hand = EMPTY
            return True
        return False


class WorkerPair:
    """
    A pair of workers, one going up and the other going down compared to the conveyor belt.
    """
    def __init__(self, index: int, slots: list[str]):
        self.up = Worker(index, Worker.UP, slots)
        self.down = Worker(index, Worker.DOWN, slots)

    def work(self) -> bool:
        """
        Make the workers work.
        :return: True if any of the workers changed the assembly line, False otherwise.
        """
        workers: list[Worker] = [self.up, self.down]
        shuffled: list[Worker] = random.sample(workers, len(workers))
        result: bool = False
        for worker in shuffled:
            if worker.work():
                result = True
                break
        return result
