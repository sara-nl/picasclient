# %% [markdown]

## Use PiCaS to run local tasks

### Outline
# - Ensure the environment is set up correctly.
# - Set up a simple problem
# - Create tokens and push them to the database
# - Run the tasks locally using PiCaS by pulling tokens from the database

### references
# - the main couchdb database: https://picas.surfsara.nl:6984
# - the couchdb web ui login page: https://picas.grid.sara.nl:6984/_utils/#login
# - the couchdb database for your project: https://picas.grid.sara.nl:6984/_utils/#database/<my_project_db>/_all_docs
# - the push token example https://github.com/sara-nl/picasclient/blob/master/examples/pushTokens.py
# - the run local examples script https://github.com/sara-nl/picasclient/blob/master/examples/local_example.py

### Minimum requirements
# - a configured environemt with login credentials and the picas configuration file
# - The previous to notebooks: 00-environment-setup and 01-database-setup should have been run.
# - cd ~/workspaces/surf/picas/picasclient
# - source .venv/picas-tutorial/bin/activate

# %%
%cd ~/workspaces/surf/picas

# %%
! mkdir example_02

# %% [markdown]
## Initialize the picas configuration (if not already done)
# See the 01-database-setup ( ..todo:: add hyperlink) notebook for details on how to do this.

# %% [markdown]
### Hello world PiCaS example
# The simplest problem that can be run locally is to pass parameters (tokens) to a script and run it.
# The example below depicts a typical workflow on a cluster, i.e a script that accepts one or more
# parameters and runs a command with those parameters within the pilot job (that is already allocated
# and running on the cluster). In the example below the script is run locally. In the next tutorials
# the jobs will be run on a cluster using slurm.
#
# The steps and components are:
#   - The script that runs a tasks (e.g. `process_task.sh`): just accept the input parameters and print them.
#   - The set of parameters (tokens) that first need to be pushed to the database, e.g quickExamples.txt
#   - The script that pushes the tokens to the database ( e.g. `pushTokens.py`).
#   - The script that is executed locally that pulls the tokens from the database and runs the task (e.g. `local_example.py`).

# %% [markdown]
#### The script that runs a task: process_task.sh

# %%
%%writefile example_02/process_task.sh
#!/bin/bash

#@helpdesk: SURF helpdesk <helpdesk@surf.nl>
#
# usage: ./process_task.sh [input] [tokenid]

# enable verbosity
set -x

# obtain/dump the information for the Worker Node to stdout
echo ""
echo `date`
echo ${HOSTNAME}

# initialize job arguments
INPUT=$1
TOKENID=$2
OUTPUT=output_${TOKENID}
echo $INPUT
echo $TOKENID
echo $OUTPUT

#
# start processing
#

# short example, just echo the input
# use this command for the short example
bash -c "$INPUT"

# display the end date
echo `date`

exit 0

# %% [markdown]
#### Define the bunch of parameters for the tasks.
# In the file below, each line is one parameter of the task. This file will be processed by the
# push tokens script and the content of the file will be translated into tokens to be consumed
# later on by the main run script that pulls the tokens and dispatches them as tasks in the pilot
# allocated resources.

# %%
%% writefile example_02/quickExample.txt
echo 'this is token A'
echo 'this is token B'
echo 'this is token C'


# %% [markdown]
# The push tokens script

# %%
%% writefile example_02/pushTokens.py

# .. todo Mher:: add a proper argument parser
'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushTokens.py <example>
description:
   Connects to PiCaS server
   Creates tokens for <example>: "quick", "fractals, or "autopilot"
   Loads the tokens to the database
'''

import sys
import subprocess
import picasconfig
from picas.clients import CouchDB
from picas.documents import Task


def createTokens(fields):
    tokens = []
    i = db.doc_count()
    for arg in fields:
        for line in fields[arg]:
            token = {
                '_id': 'token_' + str(i),
                'type': 'token',
                arg : line,
            }
            tokens.append(Task(token))
            i = i + 1
    return tokens

if __name__ == '__main__':

    # Choose for which example you are creating tokens
    if len(sys.argv) == 2:
        example = sys.argv[1]
    else:
        exit('Please give example as commandline argument. Options are "quick", "fractals, or "autopilot".')

    # Create a connection to the server
    db = CouchDB(
        url=picasconfig.PICAS_HOST_URL,
        db=picasconfig.PICAS_DATABASE,
        username=picasconfig.PICAS_USERNAME,
        password=picasconfig.PICAS_PASSWORD)

    # Create tokens
    if example == "quick":
        # create tokens with inputs given in file
        tokensfile = "quickExample.txt"
        with open(tokensfile) as f:
            fields = {"input": f.read().splitlines()}
        tokens = createTokens(fields)
    elif example == "fractals":
        tokensfile = subprocess.check_output("./createTokens", text=True).rstrip('\n')
        with open(tokensfile) as f:
            fields = {"input": f.read().splitlines()}
        tokens = createTokens(fields)
    elif example == "autopilot":
        # create tokens with number of cores specified
        fields = {"cores": [ 1, 1, 4]}
        tokens = createTokens(fields)
        for token in tokens:
            token.input = "echo $SLURM_CPUS_PER_TASK"
    else:
        exit('Unknown example. Options are "quick", "fractals, or "autopilot".')

    # Save tokens in database
    db.save_documents(tokens)


# %% [markdown]
# The picas local_example.py orchestrator script

# %%
%% writefile example_02/local_example.py
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
    parser = argparse.ArgumentParser(description="Arguments used in the different classes in the example.")
    parser.add_argument("--design_doc", default="Monitor", type=str, help="Select the designdoc used by the actor class")
    parser.add_argument("--view", default="todo", type=str, help="Select the view used by the actor class")
    parser.add_argument("-v", "--verbose", action="store_true", help="Set verbose")
    return parser


class ExampleActor(RunActor):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Feel free to adjust to whatever you need, a template can be found at: example-template.py
    """
    def __init__(self, db, modifier, view="todo", **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        # self.iterator = EndlessViewIterator(self.iterator)
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
        command = ["/usr/bin/time", "./process_task.sh", token['input'], token['_id']]
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
    actor = ExampleActor(client, modifier, view=args.view, design_doc=args.design_doc)

    # Start work!
    actor.run(max_token_time=1800, max_total_time=3600, max_tasks=10, max_scrub=2)

if __name__ == '__main__':
    main()
