import pytest
import signal
import subprocess
import time
import unittest

from test_mock import MockDB, MockRun, MockRunWithStop, MockRunEmpty
from unittest.mock import patch

from picas import actors
from picas.documents import Task


class TestRun(unittest.TestCase):

    def _callback(self, task):
        """
        _callback is used to process tasks: for mock tasks it just increases the counter.
        """
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1
        task['exit_code'] = 0

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
        """
        Test to stop after 1 task is performed.
        """
        self.count = 0
        self.test_number = 1
        runner = MockRunWithStop(self._callback)
        runner.run(max_tasks=self.test_number)
        self.assertEqual(self.count, self.test_number)

    def stop_fn(self, run_obj, id):
        return run_obj.current_task['_id'] == id

    def test_stop_fn(self):
        """
        Test to stop when a function is true.
        """
        self.count = 0
        self.stop_fn_arg = "a"
        runner = MockRunWithStop(self._callback)
        runner.run(stop_function=self.stop_fn, run_obj=runner, id=self.stop_fn_arg)
        self.assertEqual(runner.current_task['_id'], self.stop_fn_arg)

    def _callback_timer(self, task):
        """
        Callback function for processing tokens that sleeps, s.t. the max time of
        processing can expire and stop the processing.
        """
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1
        time.sleep(0.5)  # force one token to "take" 0.5 s
        task['exit_code'] = 0

    def test_max_total_time(self):
        """
        Test to stop running when the max time is about to be reached.
        """
        self.count = 0
        max_time = 1.
        runner = MockRunWithStop(self._callback_timer)
        start = time.time()
        runner.run(max_total_time=max_time)
        end = time.time()
        exec_time = end-start
        self.assertAlmostEqual(max_time, exec_time, 1)

    def test_max_total_time_empty(self):

        self.count = 0
        max_time = 1.
        runner = MockRunEmpty(self._callback_timer)
        start = time.time()
        runner.run(max_total_time=max_time)
        end = time.time()
        exec_time = end-start
        self.assertAlmostEqual(max_time, exec_time, 1)

    def _callback_error(self, task):
        """
        Callback function that simulates an error.
        """
        self.assertTrue(task.id in [t['_id'] for t in MockDB.TASKS])
        self.assertTrue(task['lock'] > 0)
        self.count += 1
        task['exit_code'] = 1

    def test_scrub(self):
        """
        Test how many times a token is scrubbed. We can only test max_scrub
        0 or 1 because of the limitations of MockDB.
        """
        self.count = 0
        max_scrub = 0
        runner = MockRunWithStop(self._callback_error)
        runner.run(max_scrub=max_scrub)
        for t in runner.db.saved:
            self.assertEqual(runner.db.saved[t]["scrub_count"], max_scrub)
        max_scrub = 1
        runner = MockRunWithStop(self._callback_error)
        runner.run(max_scrub=max_scrub)
        for t in runner.db.saved:
            self.assertEqual(runner.db.saved[t]["scrub_count"], max_scrub)

    @patch('picas.actors.log')
    @patch('signal.signal')
    def test_setup_handler(self, sig, log):
        """
        Test the setting up of the handler.
        """
        actor = actors.RunActor(MockDB())
        actor.setup_handler()

        sig.assert_any_call(signal.SIGTERM, actor.handler)
        sig.assert_any_call(signal.SIGINT, actor.handler)
        log.info.assert_any_call('Setting up signal handlers')


class TestHandler(unittest.TestCase):

    def setUp(self):
        self.lock_code = 2
        self.done_code = 2
        self.actor = actors.RunActor(MockDB(), token_reset_values=[self.lock_code, self.done_code])
        self.actor.subprocess = subprocess.Popen(['sleep', '10'])  # ensure the actor is busy
        self.actor.current_task = Task({'_id': 'c', 'lock': None, 'done': None})

    def test_signal_handling(self):
        """
        Test the handler response: proper exiting and updating of task codes.
        """
        self.actor.setup_handler()

        # to handle the exit code from the handler, pytest can catch it
        with pytest.raises(SystemExit) as handler_exit_code:
            self.actor.handler(signal.SIGTERM, None)
        self.assertEqual(handler_exit_code.value.code, 0)

        with pytest.raises(SystemExit) as handler_exit_code:
            self.actor.handler(signal.SIGINT, None)
        self.assertEqual(handler_exit_code.value.code, 0)

        self.assertEqual(self.actor.current_task['lock'], self.lock_code)
        self.assertEqual(self.actor.current_task['done'], self.done_code)
