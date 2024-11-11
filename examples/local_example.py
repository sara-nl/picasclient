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

import logging
import os
import time
import couchdb

from picas.actors import RunActor
from picas.clients import CouchDB
from picas.executers import execute
from picas.iterators import TaskViewIterator
from picas.iterators import EndlessViewIterator
from picas.modifiers import BasicTokenModifier
from picas.util import Timer
from . import picasconfig

log = logging.getLogger(__name__)

class ExampleActor(RunActor):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Feel free to adjust to whatever you need, a template can be found at: example-template.py
    """
    def __init__(self, db, modifier, view="todo", **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.iterator = EndlessViewIterator(self.iterator)
        self.modifier = modifier
        self.client = db

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " +token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")

        # Start running the main job, the logging is done internally and saved below
        # /usr/bin/time -v ./process_task.sh [input] [tokenid]
        command = ["/usr/bin/time", "-v", "./process_task.sh", token['input'], token['_id']]
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
    # setup connection to db
    client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create actor
    actor = ExampleActor(client, modifier)
    # Start work!
    actor.run(max_token_time=10, max_total_time=100, max_tasks=10, max_scrub=2)

if __name__ == '__main__':
    main()
