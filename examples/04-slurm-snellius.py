# %% [markdown]

## Use PiCaS to run tasks on Snellius

### Outline
# - Set up a non trivial example - the fractals example
# - Create tokens and push them to the database
# - Run the tasks on Snellius using PiCaS by pulling tokens from the database

### references
# - 02-local-run.ipynb notebook

### Minimum requirements
# - you have run the 02-local-run.ipynb notebook and have a working PiCaS database
# - you have access to Snellius

# %%
%cd ~/picas
! ls

# %%
! mkdir example_04

# %% [markdown]
### First we need to define / create the tokens for the Fractals example.
# The "create_tokens" script creates tokens and puts them in a temporary file
# The expected content of the file are similar to the following:
#
#   ```
#   -q 0.100 -d 256 -m 400
#   -q 0.100 -d 256 -m 4400
#   -q 0.100 -d 256 -m 8400
#   -q 0.100 -d 2280 -m 400
#   -q 0.100 -d 2280 -m 4400
#   -q 0.100 -d 2280 -m 8400
#   -q 0.100 -d 4304 -m 400
#   ```
# These are parameters that will be passed to the executable that will be run for each token.
# (just for eyeballing purposes)
# %%
! cd examples
! ./create_tokens

# check the content of the created tokens file that is created (last file in ls -ltr)
! ls -ltr /tmp | tail -n 1 | awk '{print $9}' | xargs -I {} cat /tmp/{}

# %% [markdown]
# Next we need to push the tokens to the database, we reuse the create_token function for
# the 02 example.

# %%
import subprocess
import picasconfig
from picas.clients import CouchDB
from picas.documents import Task

def create_tokens(fields: dict) -> list:
    """
    Create the tokens as a list of Task documents.

    The fields parameter is a dictionary where keys are field names and values are
    lists of input values. For every 'input' value a unique id is assigned and the
    corresponding input value is used to create a token.

    For example, the following becomes a list of tokens:
     {'input': [
        "echo 'this is token A'",
        "echo 'this is token B'",
        "echo 'this is token C'"]
     }


    :param fields: A dictionary where keys are field names and values are lists of input values.
    :return: A list of Task documents representing the tokens. For the example above,
      it would return a list of three Task objects with .id attributes set to
      'token_0', 'token_1', and 'token_2' respectively and .input attributes of each set to
      "echo 'this is token A'", "echo 'this is token B'", and "echo 'this is token C'".
    """
    tokens = []
    n_docs = db.doc_count()
    for arg in fields:
        for line in fields[arg]:
            token = {
                '_id': 'token_' + str(n_docs),
                'type': 'token',
                arg: line,
            }
            tokens.append(Task(token))
            n_docs += 1

    return tokens

# %% [markdown]
# read the tokens from the file in /tmp and push them to the database

# %%
tokensfile = subprocess.check_output("./createTokens", text=True).rstrip('\n')
with open(tokensfile) as fobj:
    fields = {"input": fobj.read().splitlines()}
    tokens = create_tokens(fields)

# create a connection to the server
db = CouchDB(
    url=picasconfig.PICAS_HOST_URL,
    db=picasconfig.PICAS_DATABASE,
    username=picasconfig.PICAS_USERNAME,
    password=picasconfig.PICAS_PASSWORD)


# save tokens in database
db.save_documents(tokens)

# %% [markdown]
# Compile and build the executable that runs the non trivial fractals code

# %%
! cc src/fractals.c -o bin/fractals -lm

# %% [markdown]
#### The script that runs a fractals task: process_task.sh
# The script basically accepts the tokens as input command line parameters.
# The following is done in the script:
#  - display the node name and date
#  - initialize the job arguments and echo them (for verbosity)
#  - for the sake of demonstration, run the input command as a bash command
#  - wrap up the job by displaying the end date and exit code

# %%
%%writefile example_04/process_task.sh
#!/bin/bash

# usage
#  ./process_task.sh <input_command> <token_id>
#  ./process_task.sh 'sleep 1' my_token_id
# enable verbosity
#set -x

# obtain/dump the information for the Worker Node to stdout
echo ""
echo `date`
echo ${HOSTNAME}

# initialize job arguments
INPUT_CMD=$1
TOKENID=$2
OUTPUT=output_${TOKENID}
echo "----------- input argument ----------------"
echo "Input command: ${INPUT_CMD}"
echo "Token ID: ${TOKENID}"
echo "Output file: ${OUTPUT}"
echo "------------ end input argument ---------------"

#
# start processing
#

# short example, just echo the input
# use this command for the short example, replace this with something else
# that does fancy things for a real life application
# .. just run something, dummy task
echo "----------------- start execute task --------------------------------"
bin/fractals -o $OUTPUT $INPUT
echo "----------------- end execute task --------------------------------"

# display the end date
echo `date`

exit 0

# %%
# set the execute permission on the script
! chmod +x example_04/process_task.sh

# %% [markdown]
### Create the job script that will allocate the pilot job and run the tasks

# %%
%%writefile example_04/slurm_example.sh
#!/bin/bash
#SBATCH --array=0-5
#SBATCH -t 00:30:00
#SBATCH -p rome

#how to use this example:
#1.clone the Picasclient github
#git clone https://github.com/sara-nl/picasclient.git
#cd picasclient
#2.install packages
#pip install picas
#3.create examples/picasconfig.py using template picasconfig_example.py
#4.submit pilot job
#sbatch snellius-example.sh
#ALERT: The minimal allocation on Snellius is 16 cores.


## adding software modules load for Snellius
module load 2024
module load Python/3.12.3-GCCcore-13.3.0
pip install --user picas


# You may set environmental variables needed in the SLURM job
# For example, when using the LUMI container wrapper:
# export PATH="/path/to/install_dir/bin:$PATH"
python local_example.py


# %% [markdown]
### Use the existing local_example.py script to run the tasks
# %%
%%writefile example_04/local_example.py
"""
usage: python local_example.py
description:
    Connect to PiCaS server
    Get the next token in todo View
    Fetch the token parameters, e.g. input value
    Run main job (process_task.sh) with the input argument
    When done, return the exit code to the token
    Attach the logs to the token
"""
import argparse
import logging
import time
import picasconfig

from picas.actors import RunActor
from picas.clients import CouchDB
from picas.executers import execute
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

    # create the token modifier
    modifier = BasicTokenModifier()

    # create the actor
    actor = ExampleActor(client, modifier, view=args.view, design_doc=args.design_doc)

    # start the work!
    actor.run(max_token_time=1800, max_total_time=3600, max_tasks=10, max_scrub=2)

if __name__ == '__main__':
    main()

# %% [markdown]
# Now you can submit the job to Snellius with:

# %%
! cd example_04 && sbatch slurm_example.sh