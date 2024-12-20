# -*- coding: utf-8 -*-
"""
@author: Jan Bot
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
"""

import time

from couchdb.http import ResourceConflict

from .documents import Task
from .picaslogger import picaslogger


class ViewIterator:
    """
    Dummy class to show what to implement for a PICaS iterator.
    """

    def __init__(self):
        self._stop = False

    def __iter__(self):
        """Python needs this."""
        return self

    def reset(self):
        """Reset the iterator."""
        self._stop = False

    def stop(self):
        """Stop the iterator."""
        self._stop = True

    def is_stopped(self):
        """Bool: iterator stopped."""
        return self._stop

    def __next__(self):
        """
        Get the next task.
        @throws: StopIteration: if no more items are available
        @throws: EnvironmentError: if there is too much contention to
                                   lock an item for use.
        """
        if self.is_stopped():
            raise StopIteration

        try:
            return self.claim_task()
        except IndexError as ex:
            self.stop()
            raise StopIteration from ex

    def claim_task(self):
        """Get the first available task from a view."""
        raise NotImplementedError("claim_task function not implemented.")

    def reconnect(self, database):
        """Reconnect to database"""
        self.database = database


def _claim_task(database, view, allowed_failures=10, **view_params):
    for _ in range(allowed_failures):
        try:
            doc = database.get_single_from_view(view, window_size=100,
                                                **view_params)
            task = Task(doc)
            return database.save(task.lock())
        except ResourceConflict:
            pass
    raise EnvironmentError("Unable to claim task.")


class TaskViewIterator(ViewIterator):

    """Iterator object to fetch tasks while available."""
    def __init__(self, database, view, **view_params):
        """
        @param database: CouchDB database to get tasks from.
        @param view: CouchDB view from which to fetch the task.
        @param view_params: parameters which need to be passed on to the view
        (optional).
        """
        super().__init__()
        self.database = database
        self.view = view
        self.view_params = view_params

    def claim_task(self):
        return _claim_task(self.database, self.view, **self.view_params)


class PrioritizedViewIterator(ViewIterator):
    """
    Iterator object to fetch tasks while available, first from a high
    priority view and then from a low priority view.
    """

    def __init__(self, database, high_priority_view, low_priority_view,
                 **view_params):
        """
        @param database: CouchDB database to get tasks from.
        @param high_priority_view: CouchDB view from which to fetch tasks
               first.
        @param low_priority_view: CouchDB view to get tasks from if no high
                                  priority tasks are available.
        @param view_params: parameters which need to be passed on to the view
        (optional).
        """
        super().__init__()
        self.database = database
        self.high_priority_view = high_priority_view
        self.low_priority_view = low_priority_view
        self.view_params = view_params

    def claim_task(self):
        try:
            return _claim_task(self.database, self.high_priority_view,
                               **self.view_params)
        except IndexError:
            # don't catch the second IndexError:
            # if both views are empty, fail.
            return _claim_task(self.database, self.low_priority_view,
                               **self.view_params)


class EndlessViewIterator(ViewIterator):
    """
    Iterator that will endlessly fetch tasks from a ViewIterator, sleeping
    when none are available.
    """
    def __init__(self, view_iterator, sleep_sec=10, stop_callback=None,
                 **stop_callback_args):
        """
        @param view_iterator: ViewIterator to get actual tasks from.
        @param sleep_sec: number of seconds to wait before trying the
                          view_iterator again. Set to 0 to do a busy wait.
        @param stop_callback: callback function to determine whether this
                              iterator should stop feeding tasks
        @param stop_callback_args: arguments to the stop_callback function.
        """
        super().__init__()
        self.iterator = view_iterator
        self.sleep_sec = sleep_sec
        self.stop_callback = stop_callback
        self.stop_callback_args = stop_callback_args

    def is_cancelled(self):
        """Bool to check if the while should be stopped"""
        return (self.is_stopped() or
                (self.stop_callback is not None and
                 self.stop_callback(**self.stop_callback_args)))

    def __next__(self):
        while not self.is_cancelled():
            try:
                return next(self.iterator)
            except StopIteration:
                self.iterator.reset()
                time.sleep(self.sleep_sec)
                picaslogger.info("Iterator is waiting for work...")

        # no longer continue
        self.iterator.stop()
        self.stop()
        picaslogger.info("Iterator is finishing.")
        raise StopIteration
