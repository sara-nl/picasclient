'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python local_example.py
description:
    Connect to PiCaS server
    Get the next token in todo View
    Fetch the token parameters, e.g. input value
    Run main job (process_task.sh) with the input argument
    When done, return the exit code to the token
    Attach the logs to the token
'''

import argparse
import logging
import time
import picasconfig

from picas.actors import RunActor
from picas.clients import CouchDB
from picas.executers import execute
from picas.iterators import TaskViewIterator
from picas.iterators import EndlessViewIterator
from picas.modifiers import BasicTokenModifier
from picas.util import Timer


log = logging.getLogger(__name__)


def arg_parser():
    """
    Arguments parser for optional values of the example
    returns: argparse object
    """
    parser = argparse.ArgumentParser(
        description="Arguments used in the different classes in the example.")
    parser.add_argument(
        "-t", "--task-type", default='echo_cmd', type=str,
        help="Select the type of task to be processed")
    parser.add_argument(
        "--design_doc", default="Monitor", type=str,
        help="Select the designdoc used by the actor class")
    parser.add_argument(
        "--view", default="todo", type=str,
        help="Select the view used by the actor class")
    parser.add_argument("-v", "--verbose", action="store_true", help="Set verbose")

    return parser


class ExampleActor(RunActor):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Feel free to adjust to whatever you need, a template can be found at: example-template.py
    """
    def __init__(self, db, modifier, view="todo", task_type=None, **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        # self.iterator = EndlessViewIterator(self.iterator)
        self.modifier = modifier
        self.client = db
        self.task_type = task_type

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print(f"Working on task '{self.task_type}' with token {token['_id']}")
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")

        # Start running the main job, the logging is done internally and saved below
        command = ["/usr/bin/time", "./process_task.sh", self.task_type, token['input'], token['_id']]
        out = execute(command)

        logsout = f"logs_{token['_id']}.out"
        logserr = f"logs_{token['_id']}.err"

        # write the logs
        with open(logsout, 'w') as f:
            f.write(out[2].decode('utf-8'))
        with open(logserr, 'w') as f:
            f.write(out[3].decode('utf-8'))

        self.subprocess = out[0]

        # Get the job exit code and done in the token
        token['exit_code'] = out[1]
        token = self.modifier.close(token)

        # Attach logs in token
        curdate = time.strftime("%d/%m/%Y_%H:%M:%S_")
        try:
            log_handle = open(logsout, 'rb')
            token.put_attachment(logsout, log_handle.read())

            log_handle = open(logserr, 'rb')
            token.put_attachment(logserr, log_handle.read())
        except:
            pass


def main():
    # parse user arguments
    args = arg_parser().parse_args()

    # setup connection to db
    client = CouchDB(
        url=picasconfig.PICAS_HOST_URL,
        db=picasconfig.PICAS_DATABASE,
        username=picasconfig.PICAS_USERNAME,
        password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))

    # Create token modifier
    modifier = BasicTokenModifier()

    # Create actor
    actor = ExampleActor(client, modifier, view=args.view, design_doc=args.design_doc, task_type=args.task_type)

    # Start work!
    actor.run(max_token_time=1800, max_total_time=3600, max_tasks=10, max_scrub=2)

if __name__ == '__main__':
    main()
