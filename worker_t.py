import unittest
from workers import Worker
from constants import EMPTY, FINISHED, ASSEMBLY_DURATION

class TestWorker(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('Testing Worker class...')

    def setUp(self):
        self.slots = [EMPTY, 'A', 'B', EMPTY]
        self.worker = Worker(index=1, pos=Worker.UP, slots=self.slots)

    def tearDown(self):
        self.slots = None
        self.worker = None

    def test_initial_state(self):
        self.assertEqual(self.worker.state, Worker.State.READY)
        self.assertEqual(self.worker.left_hand, EMPTY)
        self.assertEqual(self.worker.right_hand, EMPTY)
        self.assertEqual(self.worker.assembly_remaining, 0)

    def test_pick_up_left_hand(self):
        self.assertTrue(self.worker.work())
        self.assertEqual(self.worker.state, Worker.State.LEFT_FULL)
        self.assertEqual(self.worker.left_hand, 'A')
        self.assertEqual(self.worker.right_hand, EMPTY)
        self.assertEqual(self.slots[1], EMPTY)

    def test_pick_up_right_hand(self):
        self.worker.left_hand = 'B'
        self.worker.state = Worker.State.LEFT_FULL
        self.assertTrue(self.worker.work())
        self.assertEqual(self.worker.right_hand, 'A')
        self.assertEqual(self.worker.state, Worker.State.ASSEMBLING)
        self.assertEqual(self.worker.assembly_remaining, ASSEMBLY_DURATION)
        self.assertEqual(self.slots[1], EMPTY)

    def test_start_assembling(self):
        self.worker.left_hand = 'A'
        self.worker.right_hand = 'B'
        self.worker.state = Worker.State.START_ASSEMBLING
        self.assertTrue(self.worker.work())
        self.assertEqual(self.worker.state, Worker.State.ASSEMBLING)
        self.assertEqual(self.worker.assembly_remaining, ASSEMBLY_DURATION)
        self.assertEqual(self.worker.left_hand, 'A')
        self.assertEqual(self.worker.right_hand, 'B')
        self.assertEqual(self.slots[1], 'A')

    def test_assembling(self):
        self.worker.left_hand = 'A'
        self.worker.right_hand = 'B'
        self.worker.state = Worker.State.ASSEMBLING
        self.worker.assembly_remaining = 1
        self.assertFalse(self.worker.work())
        self.assertEqual(self.worker.state, Worker.State.LEFT_EMPTY_RIGHT_FINISHED)
        self.assertEqual(self.worker.assembly_remaining, 0)
        self.assertEqual(self.worker.left_hand, EMPTY)
        self.assertEqual(self.worker.right_hand, FINISHED)
        self.assertEqual(self.slots[1], 'A')

    def test_set_finished(self):
        self.worker.left_hand = 'A'
        self.worker.right_hand = 'B'
        self.worker.state = Worker.State.ASSEMBLING
        self.worker.assembly_remaining = 1
        self.slots[1] = EMPTY
        self.assertTrue(self.worker.work())
        self.assertEqual(self.worker.state, Worker.State.READY)
        self.assertEqual(self.slots[1], FINISHED)
        self.assertEqual(self.worker.left_hand, EMPTY)
        self.assertEqual(self.worker.right_hand, EMPTY)
        self.assertEqual(self.worker.assembly_remaining, 0)

if __name__ == '__main__':
    unittest.main()