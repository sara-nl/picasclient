import unittest

from picas.generators import TokenGenerator

class TestGenerators(unittest.TestCase):

    def setUp(self):
        self.generator = TokenGenerator()

    def test_get_token(self):
        token = self.generator.get_empty_token()
        self.assertTrue(token['lock'] == 0)
        self.assertTrue(token['done'] == 0)
        self.assertTrue(token['hostname'] == '')
        self.assertTrue(token['scrub_count'] == 0)
        self.assertTrue(token['type'] == 'token')
