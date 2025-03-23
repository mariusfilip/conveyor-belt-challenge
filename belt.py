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
    UPPER_SEP: str = '+'
    LOWER_SEP: str = '~'

    def __init__(self, size: int, pretty_print: bool = False, offset: int = 2):
        """
        Create a new belt.
        :param size: the number of slots in the belt.
        :param pretty_print: whether to pretty-print the belt and the workers at each tick.
        :param offset: the number of spaces to add before each line.
        """
        self.slots: list[str] = [EMPTY] * size
        self.touched: list[bool] = [False] * size
        self.pairs: list[WorkerPair] = [WorkerPair(i, self.slots, self.touched) for i in range(size)]
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
        :return: a (d, c) pair where 'd' is a dictionary with the number of untouched components and finished products produced and 'c' is the number of changes in the belt.
        """
        result: dict[str, int] = {}
        for c in COMPONENTS + FINISHED:
            result[c] = 0
        changes: int = 0
        self._print(0, ticks)
        for i in range(ticks):
            in_c, changed, out_c, out_touched = self._tick()
            if out_c != EMPTY and (not out_touched or out_c == FINISHED):
                result[out_c] += 1
            if changed:
                changes += 1
            self._print(i + 1, ticks, in_c, out_c, out_touched)
        return result, changes

    def get_in_progress(self) -> dict[str, int]:
        """
        Get the number of untouched components in progress in the workers.
        :return: a dictionary with the number of components or finished products on the conveyor belt.
        """
        result: dict[str, int] = {}
        for c in COMPONENTS + FINISHED:
            result[c] = 0
        for i in range(len(self.slots)):
            if self.slots[i] != EMPTY and (not self.touched[i] or self.slots[i] == FINISHED):
                result[self.slots[i]] += 1
        return result

    def _tick(self) -> (str, bool, str):
        """
        Make the belt tick.
        :return: an (in, chg, out, touched) tuple where 'in' is the component that entered the belt, 'chg' is whether the belt changed, 'out' is the component that left
        the belt, and 'touched' is whether the component that left the belt was touched by a worker.
        """
        in_c, out_c, out_touched = self._shift()
        shuffled: list[WorkerPair] = random.sample(self.pairs, len(self.pairs))
        prioritized: list[WorkerPair] = sorted(shuffled, key=lambda p: p.priority, reverse=True)
        changed: bool = False
        for pair in prioritized:
            if pair.work():
                changed = True
        return in_c, changed, out_c, out_touched

    def _shift(self, refill: bool = True) -> (str, str, bool):
        """
        Shift the belt by one slot.
        :param refill: True whether to refill the first slot with a random component, False if filling it with an empty slot.
        :return: an (in, out, touched) tuple where 'in' is the component that entered the belt, 'out' is the component that left the belt, and 'touched' is whether the
        component that left the belt was touched by a worker.
        """
        out: str = self.slots[-1]
        touched: bool = self.touched[-1]
        for i in range(len(self.slots), 0, -1):
            j = i - 1
            self.slots[j] = self.slots[j - 1]
            self.touched[j] = self.touched[j - 1]
        if refill:
            self.slots[0] = random.choice(self._CHOICES)
        else:
            self.slots[0] = EMPTY
        self.touched[0] = False
        return self.slots[0], out, touched

    def _print(self, tick: int, ticks: int, inserted: str = EMPTY, generated: str = EMPTY, touched: bool = False):
        """
        Print the belt and the workers.
        :param tick: the current tick. 0 means initial state.
        :param ticks: the total number of ticks.
        :param inserted: the component that was inserted into the belt on the last tick.
        :param generated: the component or product that was generated in the last tick, if any.
        :param touched: whether the generated component was touched by a worker.
        :return:
        """
        if self.pretty_print:
            w: int = 0
            char_matrix: list[list[str]] = self._get_char_matrix()
            lines: list[str] = [''.join(row) for row in char_matrix]
            if tick > 0:
                print(f'Tick {tick}:')
            else:
                print('Initial state:')
            if inserted != EMPTY:
                s: str = f'Inserted: {inserted}'
                print(s)
                w = max(w, len(s))
            for line in lines:
                print(' ' * self.offset + line)
                w = max(w, self.offset + len(line))
            if generated != EMPTY:
                s: str = f'Generated: {generated}'
                if generated != FINISHED:
                    s += f' (touched by a worker: {touched})'
                print(s)
                w = max(w, len(s))
            if tick + 1 < ticks:
                print('=' * w)

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
            max_w_width = max(1, max_w_width)
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

        def fill_belt(matrix: list[list[str]], max_w_width: int, centre_row: int):
            """
            Fill the conveyor belt in the character matrix.
            :param matrix: character matrix to fill.
            :param max_w_width: maximum width of a worker.
            :param centre_row: row where the belt is.
            """
            # Upper horizontal line
            print_at(matrix, centre_row - 1, 0, self.UPPER_SEP * len(matrix[centre_row]))
            # The belt slots
            x = 0
            for c in self.slots:
                print_at(matrix, centre_row, x, Worker.V_SEP)
                x += 1 + 1  # separator + space
                print_at(matrix, centre_row, x, c)  # space + component + space
                x += max_w_width + 1  # worker token + space
            matrix[centre_row][-1] = Worker.V_SEP  # Rightmost sep
            # Lower horizontal line
            print_at(matrix, centre_row + 1, 0, self.LOWER_SEP * len(matrix[centre_row]))

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
