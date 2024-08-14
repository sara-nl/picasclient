"""
@author Joris Borgdorff
"""

import time
from copy import deepcopy


def merge_dicts(dict1, dict2):
    """merge two dicts"""
    merge = deepcopy(dict1)
    merge.update(dict2)
    return merge


def seconds():
    """get time in seconds"""
    return int(time.time())


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
