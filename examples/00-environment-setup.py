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

# %% [markdown]
### Setup the workspace and obtain a copy of the picas client
# %%
! mkdir -p ~/picas_tutorial

# %%
%cd ~/picas_tutorial

# %% [markdown]
### Clone the picas client repository
# %%
! git clone --branch 1.0.1 --depth 1 https://github.com/sara-nl/picasclient.git

# %%
# ensure that you are on the right branch
! git status
! ls

# %% [markdown]
### Setup virtual environment on clusters at SURF
#### [optional] if you are using your local machine you can skip this section

#### Spider

# %%
! source /cvmfs/software.eessi.io/versions/2023.06/init/bash
! module load Python/3.11.3-GCCcore-12.3.0

# %% [markdown]
#### Snellius

# %%
! module load 2024
! module load Python/3.12.3-GCCcore-13.3.0


# %% [markdown]
### Create the virtual environment and activate it
# %%
! mkdir .venv
! python3 -m venv .venv/picas-tutorial
! . .venv/picas-tutorial/bin/activate


# %% [markdown]
### Activate the environment and install picas using pip
# %%
! python3 -m pip install --upgrade pip
! pip install picas

# %% [markdown]
### [optional] Install PiCaS from the repo
# %%
! python3 -m pip install --upgrade pip
! python3 -m pip install poetry
# %%
! python3 -m poetry lock
# %%
! python3 -m poetry install

# %% [markdown]
### Next tutorials
# The upcoming tutorials are based on the picasclient [README](https://github.com/sara-nl/picasclient/blob/mher/spd-512/course-material/README.md).
#
# The notebooks contain more details and explanations that can be be executed interactively.

# %% [markdown]
### Connect / execute example notebooks on the clusters
# https://doc.spider.surfsara.nl/en/latest/Pages/jupyter_notebooks.html

#### Run a jupyter notebook server
# Install the jupyterlab package in the virtual environment

# %%
! python3 -m pip install jupyterlab

# %% [markdown]
# run the jupyterlab server, this will work on all the platforms.

# %%
! jupyter lab --no-browser --ip="127.0.0.1"

# %% [markdown]
# the expected output should be something like:
```bash
(picas-tutorial) {EESSI 2023.06} [surfadvisors-mkazandjian@ui-02 picasclient]$ jupyter lab --no-browser --ip="127.0.0.1"
[I 2025-08-25 23:50:51.633 ServerApp] jupyter_lsp | extension was successfully linked.
[I 2025-08-25 23:50:51.638 ServerApp] jupyter_server_terminals | extension was successfully linked.
[I 2025-08-25 23:50:51.644 ServerApp] jupyterlab | extension was successfully linked.
[I 2025-08-25 23:50:52.127 ServerApp] notebook_shim | extension was successfully linked.
[I 2025-08-25 23:50:52.163 ServerApp] notebook_shim | extension was successfully loaded.
[I 2025-08-25 23:50:52.165 ServerApp] jupyter_lsp | extension was successfully loaded.
[I 2025-08-25 23:50:52.167 ServerApp] jupyter_server_terminals | extension was successfully loaded.
[I 2025-08-25 23:50:52.170 LabApp] JupyterLab extension loaded from /home/surfadvisors-mkazandjian/picas_tutorial/picasclient/.venv/picas-tutorial/lib/python3.11/site-packages/jupyterlab
[I 2025-08-25 23:50:52.170 LabApp] JupyterLab application directory is /home/surfadvisors-mkazandjian/picas_tutorial/picasclient/.venv/picas-tutorial/share/jupyter/lab
[I 2025-08-25 23:50:52.171 LabApp] Extension Manager is 'pypi'.
[I 2025-08-25 23:50:52.210 ServerApp] jupyterlab | extension was successfully loaded.
[I 2025-08-25 23:50:52.210 ServerApp] Serving notebooks from local directory: /home/surfadvisors-mkazandjian/picas_tutorial/picasclient
[I 2025-08-25 23:50:52.211 ServerApp] Jupyter Server 2.17.0 is running at:
[I 2025-08-25 23:50:52.211 ServerApp] http://127.0.0.1:8888/lab?token=a9c930fe6c2d5e61845a543affac02dac7d050aeaa76a1f9
[I 2025-08-25 23:50:52.211 ServerApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
[C 2025-08-25 23:50:52.215 ServerApp]

    To access the server, open this file in a browser:
        file:///home/surfadvisors-mkazandjian/.local/share/jupyter/runtime/jpserver-1162549-open.html
    Or copy and paste one of these URLs:
        http://127.0.0.1:8888/lab?token=a9c930fe6c2d5e61845a543affac02dac7d050aeaa76a1f9
````

# %% [markdown]
# [optional]
# If you are running on a cluster you can not open the url directly in your browser.
# You can now connect to the jupyterlab server using an ssh tunnel using the command below:

# pick a random port on your local machine, e.g. 8888 (see below for a bash function that
# gives you a random port)
# %%
! ssh -L 127.0.0.1:8888:127.0.0.1:8888 my_user@spider.surf.nl -N

# %% [markdown]
# open your browser and go to the url: http://localhost:8888

# %% [markdown]
# [optional]
# If you want to find a random port on your local machine you can use the following bash

# %%
%%bash
random_unused_port ()
{
    ( netstat --listening --all --tcp --numeric | sed '1,2d; s/[^[:space:]]*[[:space:]]*[^[:space:]]*[[:space:]]*[^[:space:]]*[[:space:]]*[^[:space:]]*:\([0-9]*\)[[:space:]]*.*/\1/g' | sort -n | uniq;
    seq 1 1000;
    seq 1 65535 ) | sort -n | uniq -u | shuf -n 1
}

random_unused_port
