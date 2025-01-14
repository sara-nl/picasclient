"""
@author Joris Borgdorff
"""

import argparse
import time
from copy import deepcopy


def time_elapsed(timer, max=30.):
    """
    This function returns True whether the elapsed time is more than `max` seconds.
    @param timer: Timer
    @param max: maximum allowed time

    @returns: bool
    """
    return timer.elapsed() > max


def merge_dicts(dict1, dict2):
    """merge two dicts"""
    merge = deepcopy(dict1)
    merge.update(dict2)
    return merge


def seconds():
    """get time in seconds"""
    return int(time.time())


def arg_parser():
    """
    Arguments parser for optional values of the example
    returns: argparse object
    """
    parser = argparse.ArgumentParser(description="Arguments used in the different classes in the example.")
    parser.add_argument("--design_doc", default="Monitor", type=str, help="Select the designdoc used by the actor class")
    parser.add_argument("--view", default="todo", type=str, help="Select the view used by the actor class")
    parser.add_argument("-v", "--verbose", action="store_true", help="Set verbose")
    return parser


class Timer:
    """Timer class"""

    def __init__(self):
        self.t = time.time()

    def elapsed(self):
        """Get elapsed since class init"""
        return time.time() - self.t

    def reset(self):
        """Reset timer"""
        new_t = time.time()
        diff = new_t - self.t
        self.t = new_t
        return diff
