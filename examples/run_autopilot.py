'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage example: python core_scanner.py  --cores 1 --design_doc SingleCore
description:
    Connect to PiCaS server
    Check if there are tokens in view SingleCore/todo
    If so, submit pilot jobs to slurm
'''
import logging
import sys
import argparse

import picasconfig
from picas.picaslogger import picaslogger
from picas.clients import CouchDB
from picas.executers import execute


picaslogger.propagate = False


def arg_parser():
    """
    Arguments parser for optional values of the example
    returns: argparse object
    """
    parser = argparse.ArgumentParser(description="Arguments used in the different classes in the example.")
    parser.add_argument("--design_doc", default="Monitor", type=str, help="Select the designdoc used by the actor class")
    parser.add_argument("--view", default="todo", type=str, help="Select the view used by the actor class")
    parser.add_argument("-v", "--verbose", action="store_true", help="Set verbose")
    parser.add_argument("--cores", default=1, type=str, help="Number of cores for the job")
    parser.set_defaults(design_doc="SingleCore")

    return parser

# parse user arguments
args = arg_parser().parse_args()

# setup connection to db
client = CouchDB(
    url=picasconfig.PICAS_HOST_URL,
    db=picasconfig.PICAS_DATABASE,
    username=picasconfig.PICAS_USERNAME,
    password=picasconfig.PICAS_PASSWORD)

# check if there is work available, i.e. if there are tokens in the specified view
work_avail = client.is_view_nonempty(args.view, design_doc=args.design_doc)
if work_avail:
    picaslogger.info(f"Starting a picas clients checking view {args.view} in design document {args.design_doc}")
    command = [
        "sbatch",
        f"--cpus-per-task={args.cores}",
        f"--export=ALL,VIEW={args.view},DESIGN_DOC={args.design_doc}",
        "slurm_example.sh"
    ]
    execute(command)
else:
    picaslogger.info(f"Not starting a picas client, there is nothing to do in view {args.view} and for the design document {args.design_doc}.")
