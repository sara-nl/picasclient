import logging
import os
import time
import couchdb
import picasconfig

from picas.actors import RunActor, RunActorWithStop
from picas.clients import CouchDB
from picas.iterators import TaskViewIterator
from picas.iterators import EndlessViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute
from picas.util import Timer

log = logging.getLogger("Scrub example")

class ExampleActor(RunActorWithStop):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Example for scrubbing tokens and rerunning them.
    """
    def __init__(self, db, modifier, view="todo", scrub_count=2, **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.iterator = EndlessViewIterator(self.iterator)
        self.modifier = modifier
        self.client = db
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

        if (token['scrub_count'] < self.scrub_limit) and (out[1] != 0):
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

    def time_elapsed(self, elapsed=30.):
        """
        This function returns whether the class has been alive for more than `elapsed` seconds. This is needed because currently the maxtime argument in RunActor.run is broken:
        The run method will break when the iterator is non-empty and then it checks if the maxtime has passed. If the iterator stays empty, it will run until a new token is 
        processed, and after processing the if statement is true, and run breaks.

        @param elapsed: lifetime of the Actor in seconds

        @returns: bool
        """
        return self.timer.elapsed() > elapsed

def main():
    # setup connection to db
    client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create actor
    actor = ExampleActor(client, modifier, scrub_count=2)
    # Start work!
    actor.run()

if __name__ == '__main__':
    main()
