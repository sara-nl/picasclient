# -*- coding: utf-8 -*-

import logging
import sys

import picasconfig
from picas.picaslogger import picaslogger
from picas.clients import CouchDB
from picas.executers import execute
from picas.util import arg_parser

picaslogger.propagate = False

# expand the parser for the example
parser = arg_parser()
parser.add_argument("--cores", default=1, type=str, help="Number of cores for the job")
parser.set_defaults(design_doc="SingleCore")
args = arg_parser().parse_args()

client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)

work_avail = client.is_view_nonempty(args.view, design_doc=args.design_doc)
if work_avail:
    picaslogger.info(f"Starting a picas clients checking view {args.view} in design document {args.design_doc}")
    command = ["sbatch", f"--cores {args.cores}", f"--export=VIEW={args.view},DOC={args.design_doc}", "N-core-job.sh"]
    execute(command)
else:
    picaslogger.info(f"Not starting a picas client, there is nothing to do in view {args.view} and for the designdocs {args.design_doc}.")
