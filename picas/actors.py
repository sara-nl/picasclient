# -*- coding: utf-8 -*-
"""
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
@author: Jan Bot, Joris Borgdorff
"""
import logging

from .util import Timer
from .iterators import TaskViewIterator, EndlessViewIterator

from couchdb.http import ResourceConflict


class RunActor(object):
    """
    Executor class to be overwritten in the client implementation.
    """

    def __init__(self, db, iterator=None, view='todo', **view_params):
        """
        @param database: the database to get the tasks from.
        """
        if db is None:
            raise ValueError("Database must be initialized")
        self.db = db
        self.tasks_processed = 0

        self.iterator = iterator
        if iterator is None:
            self.iterator = TaskViewIterator(self.db, view, **view_params)
        else:
            self.iterator = iterator

    def _run(self, task):
        """
        Execution of the work on the iterator used in the run method.
        """
        self.prepare_run()

        try:
            self.process_task(task)
        except Exception as ex:
            msg = ("Exception {0} occurred during processing: {1}"
                   .format(type(ex), ex))
            task.error(msg, exception=ex)
            print(msg)

        while True:
            try:
                self.db.save(task)
                break
            except ResourceConflict:
                # simply overwrite changes - model results are more
                # important
                new_task = self.db.get(task.id)
                task['_rev'] = new_task.rev

        self.cleanup_run()
        self.tasks_processed += 1


    def run(self):
        """
        Run method of the actor, executes the application code by iterating
        over the available tasks in CouchDB.
        """
        time = Timer()
        self.prepare_env()
        try:
            for task in self.iterator:
                self._run(task)
        finally:
            self.cleanup_env()

    def prepare_env(self, *args, **kwargs):
        """
        Method to be called to prepare the environment to run the
        application.
        """
        pass

    def prepare_run(self, *args, **kwargs):
        """
        Code to run before a task gets processed. Used e.g. for fetching
        inputs.
        """
        pass

    def process_task(self, task):
        """
        The function to override, which processes the tasks themselves.
        @param task: the task to process
        """
        raise NotImplementedError

    def cleanup_run(self, *args, **kwargs):
        """
        Code to run after a task has been processed.
        """
        pass

    def cleanup_env(self, *args, **kwargs):
        """
        Method which gets called after the run method has completed.
        """
        pass

class RunActorWithStop(RunActor):
    """
    RunActor class with added stopping functionality.
    """

    def run(self, maxtime=None, avg_time_factor=0.0, max_tasks=0, stop_function=None, **stop_function_args):
        """
        Run method of the actor, executes the application code by iterating
        over the available tasks in CouchDB, including stop logic. The stop
        logic is also extended into the EndlessViewIterator to break it when
        the condition is met, otherwise it never stops.
        """
        time = Timer()
        self.prepare_env()
        # Special case to break the while loop of the EndlessViewIterator: 
        # The while loop cant reach the stop condition in the for loop below, 
        # so pass the condition into the stop mechanism of the EVI, then the
        # iterator is stopped from EVI and not the RunActorWithStop
        if isinstance(self.iterator, EndlessViewIterator):
            self.iterator.stop_callback = stop_function
            self.iterator.stop_callback_args = stop_function_args
        try:
            for task in self.iterator:
                self._run(task)

                logging.debug("Tasks executed: ", self.tasks_processed)

                if (stop_function is not None and 
                    stop_function(**stop_function_args)):
                    break

                # break if number of tasks processed is max set
                if max_tasks and self.tasks_processed == max_tasks:
                    break

                if maxtime is not None:
                    will_elapse = ((avg_time_factor + self.tasks_processed) *
                                   time.elapsed() / self.tasks_processed)
                    if will_elapse > maxtime:
                        break
        finally:
            self.cleanup_env()
