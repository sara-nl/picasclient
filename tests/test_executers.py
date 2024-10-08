import unittest

from picas.executers import execute


class TestExecutors(unittest.TestCase):

    def test_run_command(self):
        proc, returncode, stdout, stderr = execute(["echo", "'hello world'"])

        self.assertEqual(returncode, 0)
        self.assertEqual(stdout, b"'hello world'\n")
        self.assertEqual(stderr, b'')
