# -*- coding: utf-8 -*-

import logging
import sys

import picasconfig
from picas.picaslogger import picaslogger
from picas.clients import CouchDB
from picas.executers import execute

picaslogger.propagate = False

client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
work_1c_avail = client.is_view_nonempty("todo1c", design_doc="MonitorCores")
work_4c_avail = client.is_view_nonempty("todo4c", design_doc="MonitorCores")

if work_1c_avail and work_4c_avail:
    picaslogger.info(f"Starting a picas clients checking view todo1c and view todo4c")
    command = ["sbatch", "single-core-job.sh"]
    execute(command)
    command = ["sbatch", "multi-core-job.sh"]
    execute(command)
elif work_1c_avail:
    picaslogger.info(f"Starting a picas client checking view todo1c")
    command = ["sbatch", "single-core-job.sh"]
    execute(command)
elif work_4c_avail:
    picaslogger.info(f"Starting a picas client checking view todo4c")
    command = ["sbatch", "multi-core-job.sh"]
    execute(command)
else:
    picaslogger.info(f"Not starting a picas client, there is nothing to do in views todo1c and todo4c")
