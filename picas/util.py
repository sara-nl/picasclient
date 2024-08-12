import time
from copy import deepcopy

''' @author Joris Borgdorff '''


def merge_dicts(dict1, dict2):
    merge = deepcopy(dict1)
    merge.update(dict2)
    return merge


def seconds():
    return int(time.time())


class Timer:

    def __init__(self):
        self.t = time.time()

    def elapsed(self):
        return time.time() - self.t

    def reset(self):
        new_t = time.time()
        diff = new_t - self.t
        self.t = new_t
        return diff
