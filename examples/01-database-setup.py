# %% [markdown]

## Setup and connect to the Picas database

### Outline
# - Initialize the Picas configuration using the `picas exec` CLI.
# - Change the Picas CouchDB password using the `picas exec` CLI.
# - Create the DB views

### references
# - the main couchdb database: https://picas.surfsara.nl:6984
# - the couchdb web ui login page: https://picas.grid.sara.nl:6984/_utils/#login
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

### Minimum requirements + summary of steps to run this notebook
# - Make sure that the [00-environment-setup](https://github.com/sara-nl/picasclient/blob/mher/spd-512/course-material/examples/notebooks/00-environment-setup.ipynb) notebook has been executed and that the virtual
#   environment is activated.
# - cd ~/picas_tutorial/picasclient
# - source .venv/picas-tutorial/bin/activate
# - python3 -m poetry install
# - python3 -m pip install jupyterlab
# - jupyter lab --no-browser --ip="127.0.0.1"

# %%
%cd ~/picas_tutorial/picasclient

# %%
# ensure that the picasclient package is cloned (sanity check)
! ls -l

# %% [markdown]
## Initialize the picas configuration
### Traditional way
# The traditional way to initialize the picas configuration is to create the ``.py`` file
# with the variables defining the connection to the picas database.

# %% [markdown]
# create the examples/picasconfig.py file, in this case the password if in plain text
# %%
%%writefile examples/picasconfig.py
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE="mydatabase"
PICAS_USERNAME="myusername"
PICAS_PASSWORD="mypassword"

# %% [markdown]
### Modern way: Using the picas exec cli

# %%
# prompt the user for the picas database password (masked input)
import getpass
db_password = getpass.getpass("Enter the picas database password: ")

# %%
# you can also specify the password on the command line, but it is not recommended
! picas-cli init --host-url https://picas.surfsara.nl:6984 --database mydatabase --username myusername --password "${db_password}"

# %%
# [optional] to create the picas configuration file using the picas exec cli and input the
# password from the terminal
! picas-cli init --host-url https://picas.surfsara.nl:6984 --database mydatabase --username myusername

# %% [markdown]
## [optional] Change the picas couchdb password
# To change the password, direct interaction with the CouchDB server can be used using the couchDB
# rest API, or the picas exec cli can be used.

### [optional] Changing the password using the couchDB rest API
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

# %%
# [optional] change the password using the couchDB rest API
!username=USERNAME
!password=PASSWORD
!newpassword=NEWPASSWORD
!curl --silent --user "$username:$password" -X GET https://picas.surfsara.nl:6984/_users/org.couchdb.user:$username | jq '._rev' |  curl --user "$username:$password" -X PUT https://picas.surfsara.nl:6984/_users/org.couchdb.user:$username -H "Accept: application/json" -H "Content-Type: application/json" -H "If-Match:$(</dev/stdin)" -d '{"name":"'$username'", "roles":[], "type":"user", "password":"'$newpassword'"}'


### [optional] Changing the password using the picas exec cli
# The picas exec cli can be used to change the password, which is more convenient.
# The password is encrypted and stored in the configuration file.
# %%
# run this command in the terminal
# ! picas passwd

# %%
# the password can also be specified on the command line, but it is not recommended

# %%
import getpass
new_db_password = getpass.getpass("Enter the picas database password: ")

! picas-cli passwd --password $"{new_db_password}"

# %% [markdown]
### Create the DB views
# The views of the various documents in the database need to be created.

# Executing this script will create the following views (of documents) in the Monitor design document:
# - done
# - error
# - locked
# - todo
# - overview_total

# %%
%cd examples

# %%
! ls -l

# %%
!python create_views.py
# %% [markdown]
# To verify that the views have been created, you can login to the CouchDB web UI:
#   https://picas.grid.sara.nl:6984/_utils/#/database/mherawesomedb/_design/Monitor/_view/todo