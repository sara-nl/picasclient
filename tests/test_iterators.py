import unittest

from picas.iterators import TaskViewIterator, EndlessViewIterator
from test_mock import MockDB


class TestTask(unittest.TestCase):

    def test_taskviewiterator(self):
        self.db = MockDB()
        for task in TaskViewIterator(self.db, 'view'):
            self.assertTrue(task['lock'] > 0)
            self.assertEqual(task.rev, 'something')
            self.assertEqual(self.db.saved[task.id], task.value)
            break  # process one task only

        self.assertEqual(len(self.db.saved), 1)

    def stop_function(self, stop_value=2):
        self.stop_value=stop_value
        return len(self.db.saved) == stop_value

    def test_endlessviewiterator(self):
        self.db = MockDB()
        self.iterator = TaskViewIterator(self.db, 'view')
        for task in EndlessViewIterator(self.iterator, stop_callback=self.stop_function):
            self.assertTrue(task['lock'] > 0)
            self.assertEqual(task.rev, 'something')
            self.assertEqual(self.db.saved[task.id], task.value)

        self.assertEqual(len(self.db.saved), self.stop_value)
        self.assertEqual(len(self.db.TASKS), 3)
