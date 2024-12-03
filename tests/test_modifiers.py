import unittest

from picas.documents import Task
from picas.modifiers import BasicTokenModifier


class TestModifier(unittest.TestCase):

    def setUp(self):
        self.modifier = BasicTokenModifier()
        self.token = Task()

    def test_lock(self):
        self.modifier.lock(self.token)
        self.assertTrue(self.token['hostname'] != "")
        self.assertTrue(self.token['lock'] > 0)

    def test_unlock(self):
        self.modifier.unlock(self.token)
        self.assertTrue(self.token['hostname'] != "")
        self.assertTrue(self.token['lock'] == 0)

    def test_close(self):
        self.modifier.close(self.token)
        self.assertTrue(self.token['done'] > 0)

    def test_unclose(self):
        self.modifier.unclose(self.token)
        self.assertTrue(self.token['done'] == 0)

    def test_scrub(self):
        self.modifier.scrub(self.token)
        self.assertTrue(self.token['scrub_count'] == 1)
        self.modifier.scrub(self.token)
        self.assertTrue(self.token['scrub_count'] == 2)
        self.assertTrue(self.token['lock'] == 0)

    def test_seterror(self):
        self.modifier.set_error(self.token)
        self.assertTrue(self.token['lock'] == 99)
        self.assertTrue(self.token['done'] == 99)

    def test_addoutput(self):
        self.modifier.add_output(self.token, {"output": "test"})
        self.assertTrue(self.token['output'] == "test")
