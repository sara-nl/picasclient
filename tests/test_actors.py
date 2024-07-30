import pytest
import os
import signal
import subprocess
import time
import unittest

from test_mock import MockDB, MockRun, MockRunWithStop
from nose.tools import assert_true, assert_equals
from unittest.mock import patch, Mock

from picas import actors
from picas.documents import Task


class TestRun(unittest.TestCase):

    def _callback(self, task):
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1

    def test_run(self):
        """
        Test the run function, which iterates over the iterator class, where __next__ calls
        the claim_task method which calls _claim_task that locks the token.
        The callback function is applied through MockRun.process_task.
        This locking is the test here.
        """
        self.count = 0
        runner = MockRun(self._callback)
        runner.run()
        self.assertEqual(self.count, len(MockDB.TASKS))

    def test_stop_max_tasks(self):
        self.count = 0
        self.test_number = 1
        runner = MockRunWithStop(self._callback)
        runner.run(max_tasks=self.test_number)
        self.assertEqual(self.count, self.test_number)

    def stop_fn(self, run_obj, id):
        return run_obj.current_task['_id'] == id

    def test_stop_fn(self):
        self.count = 0
        self.stop_fn_arg = "a"
        runner = MockRunWithStop(self._callback)
        runner.run(stop_function=self.stop_fn, run_obj=runner, id=self.stop_fn_arg)
        self.assertEqual(runner.current_task['_id'], self.stop_fn_arg)

    def _callback_timer(self, task):
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1
        time.sleep(0.5) # force one token to "take" 0.5 s

    def test_max_time(self):
        self.count = 0
        self.max_time = 0.5 # one token takes 0.5, so it quits after 1 token
        self.avg_time_fac = 0.5
        self.test_number = 1
        runner = MockRunWithStop(self._callback_timer)
        runner.run(max_time=self.max_time, avg_time_factor=self.avg_time_fac)
        self.assertEqual(self.count, self.test_number)

    @patch('picas.actors.log')
    @patch('signal.signal')
    def test_setup_handler(self, mock_signal, mock_log):
        actor = actors.RunActor(MockDB())
        actor.setup_handler()

        mock_signal.assert_any_call(signal.SIGTERM, actor.handler)
        mock_signal.assert_any_call(signal.SIGINT, actor.handler)
        mock_log.info.assert_called_once_with('Setting up signal handlers')


class TestHandler(unittest.TestCase):
    def setUp(self):
        self.lock_code = 2
        self.exit_code = 2
        self.actor = actors.RunActor(MockDB(), token_reset_values=[self.lock_code, self.exit_code])
        self.actor.subprocess = subprocess.Popen(['sleep', '10']) #ensure the actor is busy
        self.actor.current_task = Task({'_id':'c', 'lock': None, 'exit_code': None})

    def test_signal_handling(self):
        self.actor.setup_handler()

        # to handle the exit code from the handler, pytest can catch it
        with pytest.raises(SystemExit) as handler_exit_code:
            self.actor.handler(signal.SIGTERM, None)
        self.assertEqual(handler_exit_code.value.code, 0)

        with pytest.raises(SystemExit) as handler_exit_code:
            self.actor.handler(signal.SIGINT, None)
        self.assertEqual(handler_exit_code.value.code, 0)

        self.assertEqual(self.actor.current_task['lock'], self.lock_code)
        self.assertEqual(self.actor.current_task['exit_code'], self.exit_code)
