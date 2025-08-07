# %% [markdown]

## Setting up the the environment for using Picas

### references
# - the official picas client repository: https://github.com/sara-nl/picasclient
# - the main couchdb database: https://picas.surfsara.nl:6984
# - the couchdb web ui login page: https://picas.grid.sara.nl:6984/_utils/#login
# - picas spider workflows: https://doc.spider.surfsara.nl/en/latest/Pages/workflows.html#picas
# - more documentation: https://doc.grid.surfsara.nl/en/latest/
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

### Minimum requirements
# It is assumed that you are running a linux like operating system where git and python3 are
# already available. The following commands should be available in your terminal:
# - `git`
# - `python3`
# - `pip3`
# - `curl`


# %% [markdown]
### Setup the workspace and obtain a copy of the picas client
# %%
! mkdir -p ~/workspaces/surf/picas

# %%
%cd ~/workspaces/surf/picas

# %% [markdown]
### Clone the picas client repository
# %%
! pwd
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
