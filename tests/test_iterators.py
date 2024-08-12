import unittest

from picas.iterators import TaskViewIterator
from test_mock import MockDB


class TestTask(unittest.TestCase):

    def test_iterator(self):
        self.db = MockDB()
        for task in TaskViewIterator(self.db, 'view'):
            self.assertTrue(task['lock'] > 0)
            self.assertEqual(task.rev, 'something')
            self.assertEqual(self.db.saved[task.id], task.value)
            break  # process one task only

        self.assertEqual(len(self.db.saved), 1)
