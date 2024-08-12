# -*- coding: utf-8 -*-
"""
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
@author: Jan Bot, Joris Borgdorff
"""
from .util import Timer
from .iterators import TaskViewIterator
from .picaslogger import picaslogger

from couchdb.http import ResourceConflict


class RunActor(object):

    """Executor class to be overwritten in the client implementation.
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

    def run(self, maxtime=None, avg_time_factor=0.0):
        """Run method of the actor, executes the application code by iterating
        over the available tasks in CouchDB.
        """
        time = Timer()
        self.prepare_env()
        try:
            for task in self.iterator:
                self.prepare_run()

                try:
                    self.process_task(task)
                except Exception as ex:
                    msg = ("Exception {0} occurred during processing: {1}"
                           .format(type(ex), ex))
                    task.error(msg, exception=ex)
                    picaslogger.info(msg)

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

                if maxtime is not None:
                    will_elapse = ((avg_time_factor + self.tasks_processed) *
                                   time.elapsed() / self.tasks_processed)
                    if will_elapse > maxtime:
                        break
        finally:
            self.cleanup_env()

    def prepare_env(self, *args, **kwargs):
        """Method to be called to prepare the environment to run the
        application.
        """
        pass

    def prepare_run(self, *args, **kwargs):
        """Code to run before a task gets processed. Used e.g. for fetching
        inputs.
        """
        pass

    def process_task(self, task):
        """The function to override, which processes the tasks themselves.
        @param task: the task to process
        """
        raise NotImplementedError

    def cleanup_run(self, *args, **kwargs):
        """Code to run after a task has been processed.
        """
        pass

    def cleanup_env(self, *args, **kwargs):
        """Method which gets called after the run method has completed.
        """
        pass
