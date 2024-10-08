# -*- coding: utf-8 -*-
"""
@author: Jan Bot
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
Module to easily execute commandline applications.
"""

# Python imports
from subprocess import Popen, PIPE
from os import system


def execute(args, shell=False):
    """Helper function to more easily execute applications.
    @param args: the arguments as they need to be specified for Popen.
    @return: a tuple containing the exitcode, stdout & stderr
    """
    with Popen(args, stdout=PIPE, stderr=PIPE, shell=shell) as proc:
        (stdout, stderr) = proc.communicate()
    return (proc, proc.returncode, stdout, stderr)


def execute_old(cmd):
    """Helper function to execute an external application.
    @param cmd: the command to be executed.
    @return the exit code of the executed program.
    """
    return system(cmd)
