# %% [markdown]

## Use PiCaS to run tasks on Snellius

### Outline
# - Overview of the problems
#    - quick example via slurm on Snellius
#    - computationally demanding example via slurm on Snellius
# - Create tokens and push them to the database
# - Run the tasks on Snellius using PiCaS by pulling tokens from the database

### references
# - 02-local-run.ipynb notebook

### Minimum requirements
# - you have run the 02-local-run.ipynb notebook and have a working PiCaS database
# - you have access to Snellius

# %%
%cd ~/picas_tutorial/picasclient/examples

# %%
! ls

# %% [markdown]
### Create the tokens for the fractals example.
# First we need to define / create the tokens for the Fractals example.
#
# The tokens are created here for demonstration purposes to show that in this case the tokens
# are arguments to the fractals executable.
#
# The "create_tokens.sh" script creates tokens and puts them in a temporary file
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
# execute the ./create_tokens.sh using
_TOKENS_FILE_PATH = !./create_tokens.sh
TOKENS_FILE_PATH = _TOKENS_FILE_PATH[0]

# %%
# show the content of the created tokens file using the variable
! cat "{TOKENS_FILE_PATH}"

# %% [markdown]
### Push the tokens to the database,

# %%
! python push_tokens.py fractals

# %% [markdown]
# Check the DB; you should see 24 new tokens in the todo [Monitor/todo](https://picas.grid.sara.nl:6984/_utils/#/database/mherawesomedb/_design/Monitor/_view/todo)

# %% [markdown]
# Compile and build the executable that runs the non trivial fractals code

# %%
! cc src/fractals.c -o bin/fractals -lm

# %%
# verify that the executable is there
! ls -l bin/fractals

# %% [markdown]
#### The script that runs a fractals task: process_task.sh
# The script accepts the tokens as input command line parameters.
# The following is done in the script:
#  - display the node name and date
#  - initialize the job arguments and echo them (for verbosity)
#  - for the sake of demonstration, run the input command as a bash command
#  - wrap up the job by displaying the end date and exit code

# %% [markdown]
# Submit the job to Snellius with:

# %%
! sbatch snellius_example.sh --task-type fractals