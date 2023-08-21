'''
@helpdesk: SURFsara helpdesk <helpdesk@surf.nl>

usage: python example_SLURM.py
description:
    Connect to PiCaS server
    Get the next token in todo View
    Fetch the token parameters, e.g. input value
    Run main job (process_task.sh) with the input argument
    When done, return the exit code to the token
    Attach the logs to the token


'''

#python imports
import os
import time
import couchdb
import picasconfig

#picas imports
from picas.actors import RunActor
from picas.clients import CouchDB
from picas.iterators import TaskViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute

class ExampleActor(RunActor):
    def __init__(self, db, modifier, view="todo", **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.modifier = modifier
        self.client = db

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " +token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")

        # Start running the main job
        # /usr/bin/time -v ./process_task.sh [input] [tokenid] 2> logs_[token_id].err 1> logs_[token_id].out
        command = "/usr/bin/time -v " +token['input'] + " 2> logs_" + str(token['_id']) + ".err 1> logs_" + str(token['_id']) + ".out"

        out = execute(command,shell=True)

        ## Get the job exit code in the token
        token['exit_code'] = out[0]
        token = self.modifier.close(token)
        #self.client.db[token['_id']] = token # necessary?

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
            print("excepted attachemnt")
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
    actor.run()

if __name__ == '__main__':
    main()
