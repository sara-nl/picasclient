import logging
import os
import time
import couchdb
import picasconfig

from picas.actors import RunActorWithStop
from picas.clients import CouchDB
from picas.iterators import EndlessViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute
from picas.util import Timer

log = logging.getLogger("Scrub with timer example")

class ExampleActor(RunActorWithStop):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Example for scrubbing tokens and rerunning them. Scrubbing is done when a token fails to finish
    within a given time limit and the user wants to rerun it.
    """
    def __init__(self, db, modifier, view="todo", time_limit=1, scrub_count=0, **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.iterator = EndlessViewIterator(self.iterator)
        self.modifier = modifier
        self.client = db
        self.time_limit = time_limit
        self.scrub_limit = scrub_count

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " +token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")

        # Start running the main job
        # /usr/bin/time -v ./process_task.sh [input] [tokenid] 2> logs_[token_id].err 1> logs_[token_id].out
        command = "/usr/bin/time -v ./process_task.sh " + "\"" +token['input'] + "\" " + token['_id'] + " 2> logs_" + str(token['_id']) + ".err 1> logs_" + str(token['_id']) + ".out"

        out = execute(command, shell=True)
        self.subprocess = out[0]

        # Get the job exit code and done in the token
        token['exit_code'] = out[1]
        token = self.modifier.close(token)

        # Scrub the token N times if it went over time, scrubbing puts it back in 'todo' state
        if (self.time_limit < self.timer.elapsed()) and (token['scrub_count'] < self.scrub_limit):
            log.info(f"Scrubbing token {token['_id']}")
            token = self.modifier.unclose(token)
            token.scrub()

        # Attach logs in token
        curdate = time.strftime("%d/%m/%Y_%H:%M:%S_")
        try:
            logsout = "logs_" + str(token['_id']) + ".out"
            log_handle = open(logsout, 'rb')
            token.put_attachment(logsout, log_handle.read())

            logserr = "logs_" + str(token['_id']) + ".err"
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
    actor = ExampleActor(client, modifier, time_limit=3, scrub_count=2)
    # Start work!
    actor.run()

if __name__ == '__main__':
    main()