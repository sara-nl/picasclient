import unittest

from test_mock import MockDB, MockRun


class TestRun(unittest.TestCase):

    def _callback(self, task):
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1

    def test_run(self):
        self.count = 0
        runner = MockRun(self._callback)
        runner.run()
        self.assertEqual(self.count, len(MockDB.TASKS))
