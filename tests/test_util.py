import unittest

from picas.util import merge_dicts, Timer
import time


class TestMerge(unittest.TestCase):

    def setUp(self):
        self.a = {'a': 1, 'b': 2}
        self.b = {'a': 2, 'c': 3}

    def test_merge_all(self):
        c = merge_dicts(self.a, self.b)
        self.assertEqual(c['a'], self.b['a'])
        self.assertEqual(self.b['a'], 2)
        self.assertEqual(self.a['a'], 1)
        self.assertEqual(len(self.a), 2)
        self.assertEqual(len(self.b), 2)
        self.assertEqual(len(c), 3)
        self.assertEqual(c['b'], self.a['b'])
        self.assertEqual(c['c'], self.b['c'])

    def test_merge_empty(self):
        c = merge_dicts(self.a, {})
        self.assertEqual(c, self.a)

    def test_empty_merge(self):
        c = merge_dicts({}, self.a)
        self.assertEqual(c, self.a)

    def test_empty_empty_merge(self):
        self.assertEqual(merge_dicts({}, {}), {})


class TestTimer(unittest.TestCase):

    def test_timer(self):
        timer = Timer()
        time.sleep(0.2)
        self.assertTrue(timer.elapsed() >= 0.2)
        self.assertTrue(timer.elapsed() < 0.4)
        timer.reset()
        self.assertTrue(timer.elapsed() < 0.2)
