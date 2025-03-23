import random
from typing import Any

from constants import EMPTY, COMPONENTS, FINISHED
from workers import Worker, WorkerPair


class Belt:
    """
    A conveyor belt that carries components to be assembled.

    It contains a list of slots that can hold components and finished products and a list of worker pairs that can assemble components.
    """
    _CHOICES: str = COMPONENTS + EMPTY

    def __init__(self, size: int, pretty_print: bool = False, offset: int = 2):
        """
        Create a new belt.
        :param size: the number of slots in the belt.
        :param pretty_print: whether to pretty-print the belt and the workers at each tick.
        :param offset: the number of spaces to add before each line.
        """
        self.slots: list[str] = [EMPTY] * size
        self.pairs: list[WorkerPair] = [WorkerPair(i, self.slots) for i in range(size)]
        self.pretty_print: bool = pretty_print
        self.offset: int = offset

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
        for c in COMPONENTS + FINISHED:
            result[c] = 0
        changes: int = 0
        self._print(0)
        for i in range(ticks):
            c, changed = self._tick()
            if c != EMPTY:
                result[c] += 1
            if changed:
                changes += 1
            self._print(i + 1, c)
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
        for i in range(len(self.slots), 0, -1):
            j = i - 1
            self.slots[j] = self.slots[j - 1]
        if refill:
            self.slots[0] = random.choice(self._CHOICES)
        else:
            self.slots[0] = EMPTY
        return result

    def _print(self, tick: int, generated: str = EMPTY):
        """
        Print the belt and the workers.
        :param tick: the current tick. 0 means initial state.
        :param generated: the component or product that was generated in the last tick, if any.
        :return:
        """
        if self.pretty_print:
            char_matrix: list[list[str]] = self._get_char_matrix()
            lines: list[str] = [''.join(row) for row in char_matrix]
            if tick > 0:
                print(f'Tick {tick}:')
            else:
                print('Initial state:')
            for line in lines:
                print(' ' * self.offset + line)
            if generated != EMPTY:
                print(f'Generated: {generated}')

    def _get_char_matrix(self) -> list[list[str]]:
        """
        Get the matrix of characters to print.
        :return: a matrix of characters to print.
        """

        def init_matrix() -> (list[list[str]], int, int):
            """
            Initialize the matrix of characters to print.
            :return: list of lists of characters, the maximum width of a worker, and the maximum height of an upper worker.
            """
            ret: list[list[str]] = []
            max_w_width: int = max(w.get_width(tokens=True) for p in self.pairs for w in (p.up, p.down))
            max_w_upper_height: int = max(p.up.get_height(tokens=True) for p in self.pairs)
            max_w_lower_height: int = max(p.down.get_height(tokens=True) for p in self.pairs)
            width: int = (1 + 1 + max_w_width + 1) * len(self.slots) + 1  # sep+space+token+space for each worker + rightmost sep
            height: int = max_w_upper_height + 1 + 1 + 1 + max_w_lower_height  # upper worker + line + slots + line + lower worker
            for _ in range(height):
                ret.append([' '] * width)
            return ret, max_w_width, max_w_upper_height

        def print_at(matrix: list[list[str]], row: int, col: int, x: Any):
            """
            Print a value at a given position in the matrix.
            :param matrix: character matrix to write to.
            :param row: row to write to.
            :param col: column to write to.
            :param x: value to write.
            """
            for i, c in enumerate(str(x)):
                matrix[row][col + i] = c

        def fill_belt(matrix: list[list[str]], max_worker_width: int, centre_row: int):
            """
            Fill the conveyor belt in the character matrix.
            :param matrix: character matrix to fill.
            :param max_worker_width: maximum width of a worker.
            :param centre_row: row where the belt is.
            """
            # Upper horizontal line
            print_at(matrix, centre_row - 1, 0, Worker.H_SEP * len(matrix[centre_row]))
            # The belt slots
            x = 0
            for c in self.slots:
                print_at(matrix, centre_row, x, Worker.V_SEP)
                print_at(matrix, centre_row, x + 1 + 1, c)  # space + component + space
                x += max_worker_width
            matrix[centre_row][-1] = Worker.V_SEP  # Rightmost sep
            # Lower horizontal line
            print_at(matrix, centre_row + 1, 0, Worker.H_SEP * len(matrix[centre_row]))

        def fill_worker(matrix: list[list[str]], worker: Worker, max_w_width: int, centre_row: int):
            """
            Fill a worker in the character matrix.
            :param matrix: character matrix to fill.
            :param worker: worker to fill into the character matrix.
            :param max_w_width: maximum width of a worker.
            :param centre_row: row where the belt is.
            """
            sign: int = 1 if worker.pos == Worker.DOWN else -1
            x = worker.index * (3 + max_w_width)
            y = centre_row + 2 * sign
            for t in worker.get_tokens(reverse=True):
                print_at(matrix, y, x, Worker.V_SEP)
                print_at(matrix, y, x + 2, t)
                y += sign
            if sign > 0:
                while y < len(matrix):
                    print_at(matrix, y, x, Worker.V_SEP)
                    y += 1
            else:
                while y >= 0:
                    print_at(matrix, y, x, Worker.V_SEP)
                    y -= 1

        def fill_pair(matrix: list[list[str]], pair: WorkerPair, max_worker_width: int, centre_row: int):
            """
            Fill a worker pair in the character matrix.
            :param matrix: character matrix to fill.
            :param pair: worker pair to fill into the character matrix.
            :param max_worker_width: maximum width of a worker.
            :param centre_row: row where the belt is.
            """
            fill_worker(matrix, pair.up, max_worker_width, centre_row)
            fill_worker(matrix, pair.down, max_worker_width, centre_row)

        def fill_pairs(matrix: list[list[str]], max_w_width: int, centre_row: int):
            """
            Fill all worker pairs into the character matrix.
            :param matrix: character matrix to fill.
            :param max_w_width: maximum width of a worker.
            :param centre_row: row where the belt is.
            """
            for pair in self.pairs:
                fill_pair(matrix, pair, max_w_width, centre_row)
            for row in range(len(matrix)):
                if centre_row - 1 <= row <= centre_row + 1:
                    pass
                else:
                    matrix[row][-1] = Worker.V_SEP

        result, max_worker_width, max_worker_upper_height = init_matrix()
        fill_belt(result, max_worker_width, max_worker_upper_height + 1)
        fill_pairs(result, max_worker_width, max_worker_upper_height + 1)
        return result
