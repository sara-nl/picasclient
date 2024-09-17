# -*- coding: utf-8 -*-
"""
@author: Jan Bot, Leiden University, Delft University of Technology, SURFsara
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
"""


# Python imports
import threading
import logging
import queue
from os import path

from .executers import execute, execute_old
from .picaslogger import picaslogger


def download(remotefile):
    """Download file"""
    logging.debug(f"Downloading: {remotefile}")
    raise NotImplementedError("Download function not implemented yet. Use SRMClient class.")


def upload(localfile):
    """Upload file"""
    logging.debug(f"Uploading: {localfile}")
    raise NotImplementedError("Upload function not implemented yet. Use SRMClient class.")


def download_many(files, poolsize=10, logger=None):
    """Download a number of files in parallel.
    @param files: an array with the locations of the files to fetch.
    @param poolsize: the number of concurrent connections that need to
    be established. Default: 10.
    @param logger: a Python logger object. Default: None.
    """
    q = queue.Queue()
    for v in files:
        q.put(v)

    thread_pool = []
    for _ in range(poolsize):
        d = Downloader(q, logger)
        d.start()
        thread_pool.append(d)

    q.join()
    for d in thread_pool:
        d.join(1)


def upload_many(files, poolsize=10):
    """Upload multiple files"""
    raise NotImplementedError("upload_many function not implemented. Use SRMClient class.")


class Downloader(threading.Thread):

    """Threaded SRM download class. Facilitates many simultaneous
     connections to the SRM. Use with care: you can easily flood the
    SRM with too many request.
    """

    def __init__(self, q, logger=None):
        """Initialization.
        @param q: Python queue object containing all the files that need
        to be downloaded.
        @param logger: Python logger object.
        """
        threading.Thread.__init__(self)
        self.q = q
        if logger is None:
            self.logger = logging.getLogger('SRM')
        else:
            self.logger = logger
        self.srm = SRMClient(self.logger)
        self.daemon = False

    def run(self):
        """Start the download worker. Starts downloading the first file
        in the queue.
        """
        while not self.q.empty():
            f = self.q.get()
            count = 0
            done = False
            while (count < 25 and not done):
                try:
                    self.srm.download(f)
                    done = True
                except Exception():
                    count += 1

            self.q.task_done()

            if count > 24:
                self.logger.error(f"Download of {f} failed after multiple tries.")
                raise EnvironmentError("Download failed of: " + f)


class SRMClient:

    """Helper class to easily down- and upload files to/from SRM.
    """

    def __init__(self, logger, host="srm://srm.grid.sara.nl/"):
        """Init function.
        @param logger: Python logger.
        @param host: host address of the SRM. Default: srm://srm.grid.sara.nl/"
        """
        self.logger = logger
        self.srm_host = host

    def remote_exists(self, loc):
        """Check if a file exists on the remote location.
        @param loc: complete path on the SRM to the file.
        @return: True when the file exists.
        """
        surl = self.srm_host + loc
        cmd = ['srmls', surl]
        picaslogger.info(" ".join(cmd))
        (proc, returncode, stdout, _) = execute(cmd)

        if returncode == 0:
            bn = path.basename(loc)
            lines = stdout.split("\n")
            for line in lines:
                if bn in line:
                    return True
        return False

    def upload(self, local_file, srm_dir, check=False):
        """Upload local file to the SRM.
        @local_file: the file that needs to be copied.
        @param srm_dir: location on the SRM where the file needs to be copied
        to.
        @param check: whether to check if the local and remote files exist.
        Default: True
        @return: location of the file on the SRM.
        """
        srm_file = path.join(srm_dir, path.basename(local_file))
        srm_url = self.srm_host + srm_file
        if check:
            if not path.isfile(local_file):
                raise EnvironmentError(10, "File not found.", local_file)
            if self.remote_exists(srm_file):
                raise EnvironmentError(11, "File exists on srm.",
                                       srm_url)

        cmd = ['srmcp', '-2', '-server_mode=passive',
               'file:///' + local_file, srm_url]
        picaslogger.info(cmd)
        (proc, returncode, _, _) = execute(cmd)
        if returncode == 0:
            pass
        else:
            raise EnvironmentError("Upload failed.")
        return srm_url

    def download(self, srm_file, local_dir="./", check=False):
        """Download a file from the SRM.
        @param srm_file: complete path to the file on the SRM.
        @param local_dir: directory where the file needs to be copied to.
        @return: location of the downloaded file.
        """
        local_file = path.join(local_dir, path.basename(srm_file))
        srm_url = self.srm_host + srm_file
        if check and not self.remote_exists(srm_file):
            raise EnvironmentError(10, "File not found.", srm_url)

        cmd = ['srmcp', '-2', '-server_mode=passive',
               srm_url, 'file:///' + local_file]
        self.logger.info("Downloading: " + local_file)
        returncode = execute_old(" ".join(cmd))
        self.logger.debug("Done downloading " + local_file)
        if returncode == 0:
            pass
        else:
            self.logger.error("Download failed of: " + srm_file)
            raise EnvironmentError("Download failed.")
        return local_file

    def remove(self, srm_file):
        """Remove a file from the SRM.
        @param srm_file: Path to the file on the SRM.
        @return: True when the operation succeeded. Throws an environment
        error otherwise.
        """
        srm_url = self.srm_host + srm_file
        cmd = ['srmrm', srm_url]
        returncode = execute_old(" ".join(cmd))
        if returncode == 0:
            pass
        else:
            self.logger.error("Removal failed of: " + srm_file)
            raise EnvironmentError("Remove failed.")
        return True
