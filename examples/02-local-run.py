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
# - Make sure that the [00-environment-setup](https://github.com/sara-nl/picasclient/blob/mher/spd-512/course-material/examples/notebooks/00-environment-setup.ipynb) notebook has been executed and that the virtual
# - Make sure that the [01-database-setup](https://github.com/sara-nl/picasclient/blob/mher/spd-512/course-material/examples/notebooks/01-database-setup.ipynb) notebook has been executed and that the virtual

# %%
%cd ~/picas_tutorial

# %%
! ls

# %% [markdown]
### Hello world PiCaS example
#
# The simplest problem that can be run locally is to pass parameters (tokens) to a script and run it.
# This approach can be generalized to run on a cluster using slurm (or other schedulers) too.
#
# In this example tokens themselves are simple echo commands that will be passed to a runner script.
#
# The steps and components are:
#   - Define / examine the set of parameters (tokens) that first need to be pushed to the database, e.g [quickExamples.txt](https://github.com/sara-nl/picasclient/blob/master/examples/quickExample.txt)
#   - Push the tokens to the database ( e.g. [push_tokens.py](https://github.com/sara-nl/picasclient/blob/master/examples/pushTokens.py) )
#   - The script that runs a tasks (e.g. [process_task.sh](https://github.com/sara-nl/picasclient/blob/master/examples/process_task.sh)): just accepts the input parameters and print them in this tutorial
#   - The runner script that is executed locally ( [local_example.py](https://github.com/sara-nl/picasclient/blob/master/examples/local_example.py) ), it pulls the tokens from the database and runs the tasks for each token.

# %%
%cd picasclient/examples

# %%
! ls -l

# %% [markdown]
#### Create the tokens
# The file quickExample.txt contains three lines with commands to be executed. You can generate three job tokens in the PiCaS DB by running

# %%
! cat quickExample.txt

# %% [markdown]
# push the tokens to the database using the push_tokens.py script

# %%
! python3 push_tokens.py quick

# %% [markdown]
# Check the DB; you should see the tokens in the view [Monitor/todo](https://picas.grid.sara.nl:6984/_utils/#/database/mherawesomedb/_design/Monitor/_view/todo)

# %% [markdown]
#### Create the tokens
# The file quickExample.txt contains three lines with commands to be executed. You can generate three job tokens in the PiCaS DB by running
# The script accepts the tokens as input command line parameters.
# The following is done in the script:
#  - display the node name and date
#  - initialize the job arguments and echo them (for verbosity)
#  - for the sake of demonstration, run the input command as a bash command
#  - wrap up the job by displaying the end date and exit code

# %% [markdown]
#### Running the tasks locally
# To run the example locally (e.g. on your laptop)

# %%
! python local_example.py

# %% [markdown]
# If all goes well, you should see output like (compare with what you see in the cell above)
#
# ```bash
# -----------------------
# Working on token: token_0
# _id token_0
# _rev 4-8b04da64c0a536bb88a3cdebe12e0a87
# type token
# lock 1692692693
# done 0
# hostname xxxxxxxxxxxx
# scrub_count 0
# input echo "this is token A"
# exit_code 0
# -----------------------
# ```
# The token in the database will have attachments with the standard and error output of the terminal. There you will find the outputfile logs_token_0.out, containing the output of the input command:
#
# ```bash
# Tue 31 Dec 2024 00:00:00 CET
# xxxxxxxxxxxx
# echo 'this is token A'
# token_0
# output_token_0
# this is token A
# Tue 31 Dec 2024 00:00:00  CET
# ```
# Once the script is running, it will start polling the PiCaS server for work. A pilot job will not die after it has completed a task, but immediately ask for another one. It will keep asking for new jobs, until all work is done, or the maximum time is up.
#
# Tokens have a status, which will go from "todo" to "done" once the work has been completed (or "error" if the work fails). To do more work, you will have to add new tokens that in the "todo" state yet, otherwise the example script will just stop after finding no more work to do. If you are interested, you can look into the scripts examples/local-example.py and examples/process_task.sh to check what the actual work is.

# %% [markdown]
### Deep-dive into the example and code explanation

#### Define the parameters that will be pushed the to database
# Fetch the PiCaS configuration and create a connection to the database

# %%
# ---------------------------
# DEVEL
# ---------------------------
# %%
%cd picas/picasclient/examples

# %%
import sys
sys.path = ['..']  + sys.path

# %%
import picas
print(picas)
# %%
# ---------------------------
# END DEVEL
# ---------------------------

# %%
from picas.picas_config import PicasConfig
from picas.crypto import decrypt_password

# %%
config = PicasConfig(load=True)
print(config)

# %%
# create a connection to the server
from picas.clients import CouchDB
from pprint import pprint

# %%
db = CouchDB(
    url=config.config['host_url'],
    db=config.config['database'],
    username=config.config['username'],
    password=decrypt_password(config.config['encrypted_password']).decode())

# %% [markdown]
# Define a bunch of parameters (echo commands) for the tasks that will be pushed as tokens to the database

token_inputs = [
    "echo 'this is token A'",
    "echo 'this is token B'",
    "echo 'this is token C'"
]

fields = {"input": token_inputs}
pprint(fields)

# %% [markdown]
# Convert the inputs to token objects that can be pushed to the database as token documents
# using the utility function create_tokens from the create_tokens.py script

# %%
from create_tokens import create_tokens
# %%
tokens = create_tokens(fields, offset=db.doc_count())
pprint(tokens)

# %% [markdown]
# The push tokens script (save them to the database)
status = db.save_documents(tokens)

# %%
# check for errors
if not any(status):
    print("Error saving tokens:")
    pprint(status)
else:
    print("Tokens saved successfully.")

# %% [markdown]
# Process the tokens by pulling tokens and using the PiCaS framework to run the tasks locally

# %%
import time
from picas.actors import RunActor
from picas.executers import execute
from picas.modifiers import BasicTokenModifier
from picas.util import Timer

# %% [markdown]
# The goal is to pass the parameters (tokens) to the .sh script and run it.
# PiCaS is responsible and will take care of fetching the tokens.
# The user's responsibility is implement the "process_task" method that PiCaS will call

# %% [markdown]
# To customize the processing, the user needs to implement the process_task method
# https://github.com/sara-nl/picasclient/blob/master/examples/example_template.py
# see actual example in the next cell

# %%
class ExampleActor(RunActor):
    """
    The ExampleActor is the custom implementation of a RunActor that the user needs for the processing.
    Feel free to adjust to whatever you need, a template can be found at: example-template.py
    """
    def __init__(self, db, modifier, view="todo", task_type=None, **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.modifier = modifier
        self.client = db
        self.task_type = task_type

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " +token['_id'])
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

# %%
# create the token modifier
modifier = BasicTokenModifier()

# %%
# create the actor
actor = ExampleActor(db, modifier, view='todo', design_doc='Monitor', task_type='echo_cmd')

# %%
# start the work!
actor.run(max_token_time=1800, max_total_time=3600, max_tasks=10, max_scrub=2)


# %% [markdown]
#  - semi-advanced example 1
#   - add an example of a top level dir that has a bunch of subdirs, each subdir has a some raw data
#   - the directory tree is traversed and each subdir is processed as a token
#   - the task would return a word count of the files in the subdir
#  - advanced example 1
#   - same as above, but the raw data is pulled from dcache
# - todo: