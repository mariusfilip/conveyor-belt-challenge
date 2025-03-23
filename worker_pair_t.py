import random
import unittest
from workers import Worker, WorkerPair
from constants import EMPTY, FINISHED

class TestWorkerPair(unittest.TestCase):

    def setUp(self):
        self.slots = [EMPTY, 'A', 'B', EMPTY]
        self.worker_pair = WorkerPair(index=1, slots=self.slots)
        self.org_seed = random.randint(1, 1000000)
        random.seed(9691)

    def tearDown(self):
        self.slots = None
        self.worker_pair = None
        random.seed(self.org_seed)

    def tearDown(self):
        self.slots = None
        self.worker_pair = None

    def test_worker_pair_work_twice(self):

        self.__worker_pair_work_once()
        self.assertFalse(self.worker_pair.work())
        self.assertEqual(self.worker_pair.up.state, Worker.State.READY)
        self.assertEqual(self.worker_pair.down.state, Worker.State.LEFT_FULL)
        self.assertEqual(self.slots[1], EMPTY)

    def test_worker_pair_no_change(self):
        self.worker_pair.up.state = Worker.State.ASSEMBLING
        self.worker_pair.down.state = Worker.State.ASSEMBLING
        self.worker_pair.up.assembly_remaining = 1
        self.worker_pair.down.assembly_remaining = 1
        self.assertFalse(self.worker_pair.work())

    def __worker_pair_work_once(self):
        self.assertTrue(self.worker_pair.work())
        self.assertEqual(self.worker_pair.up.state, Worker.State.READY)
        self.assertEqual(self.worker_pair.down.state, Worker.State.LEFT_FULL)
        self.assertEqual(self.slots[1], EMPTY)

if __name__ == '__main__':
    unittest.main()