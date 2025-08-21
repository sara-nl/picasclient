# %% [markdown]

## Set up the the environment for using Picas

### references
# - the official picas client repository: https://github.com/sara-nl/picasclient
# - the main couchdb database: https://picas.surfsara.nl:6984
# - the couchdb web ui login page: https://picas.grid.sara.nl:6984/_utils/#login
# - picas spider workflows: https://doc.spider.surfsara.nl/en/latest/Pages/workflows.html#picas
# - more documentation: https://doc.grid.surfsara.nl/en/latest/
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

### Minimum requirements (for local usage on your machine)
# It is assumed that you are running a linux like operating system where git and python3 are
# already available. The following commands should be available in your terminal:
# - `git`
# - `python3`
# - `pip3`
# - `curl`

# .. todo:: will the tutorial be given on spider? (yes, spider)
#      - publish the rendered notebooks (for the time being on github but then into the picas docs)
# .. todo:: create a module for "module load picas"
#      - look into doing that with eb
# .. todo:: add a section in the readme to bootstrap the environment for the tutorial or make this
#           a gist that can be also curled | sh
# .. todo:: explore the multi-cluster setup for picas (snellius, spider, src at the same time)
# .. todo:: add a subcommand to validate the credential by trying to connect to the database
#             $ picas-cli check

# %% [markdown]
### Setup the workspace and obtain a copy of the picas client
# %%
# .. todo:: for the final version use ~/pics_tutorial
! mkdir -p ~/workspaces/surf/picas

# %%
%cd ~/workspaces/surf/picas
! ls

# %% [markdown]
### Clone the picas client repository
# %%
! git clone https://github.com/sara-nl/picasclient.git
! ls -l picasclient

# %%
%cd picasclient
! git checkout 1.0.1

# %%
! git status
! ls

# %% [markdown]
### Create the virtual environment
# %%
! mkdir .venv
! python3 -m venv .venv/picas-tutorial

# %% [markdown]
### Install the dependencies
# %%
! .venv/picas-tutorial/bin/python3 -m pip install --upgrade pip
! .venv/picas-tutorial/bin/python3 -m pip install poetry
# %%
! .venv/picas-tutorial/bin/python3 -m poetry lock
# %%
! .venv/picas-tutorial/bin/python3 -m poetry install

# %% [markdown]
### Run the notebook in the new virtual environment
# exit the current notebook kernel and start a new one in the virtual environment

# .. todo:: add instructions and tips on how to run the notebook / jupyterlab on snellius or spider
#           e.g use surf's jupyterhub or run a jupyter server on spider and connect to it
#           or OOD