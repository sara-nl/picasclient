# -*- coding: utf-8 -*-
"""
@author: Jan Bot
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
"""


import threading
import logging
import queue

from picas import SRMClient


def download(files, threads=10):
    q = queue.Queue()
    for k, v in files.items():
        q.put(v)

    thread_pool = []
    for i in range(threads):
        d = Downloader(q)
        d.start()
        thread_pool.append(d)

    q.join()
    print("Download work done, joining threads")
    for d in thread_pool:
        print("Joining: {0!s}".format(str(d.ident)))
        d.join(1)


class Downloader(threading.Thread):

    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.q = queue
        self.logger = logging.getLogger('Pindel')
        self.srm = SRMClient(self.logger)
        self.daemon = False

    def run(self):
        while not self.q.empty():
            f = self.q.get()
            count = 0
            done = False
            while (count < 10 and not done):
                try:
                    self.srm.download(f)
                    done = True
                except Exception():
                    count += 1
            if (count > 9):
                raise EnvironmentError("Download failed.")
            self.q.task_done()
        print("Exiting while loop, thread should close itself...")
