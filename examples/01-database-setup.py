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

### Minimum requirements
# - Make sure that the 00-environment-setup notebook has been run and that the virtual environment is activated.
# - cd ~/workspaces/surf/picas/picasclient
# - source .venv/picas-tutorial/bin/activate
# - pip install notebook
# - python setup.py install
# - pip install -e .   # not sure why this is not installed the picas exec cli script
# - jupyter notebook --no-browser

# %%
! mkdir ~/workspaces/surf/picas

# %%
%cd ~/workspaces/surf/picas

# %%
! git clone https://github.com/mherkazandjian/picasclient.git

# %%
! ls -l picasclient

# %% [markdown]
## Initialize the picas configuration
### Traditional way
# The traditional way to initialize the picas configuration is to create the ``.py`` file
# with the variables defining the connection to the picas database.

# %%
%%writefile picasclient/examples/picasconfig.py
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE="mydatabase"
PICAS_USERNAME="myusername"
PICAS_PASSWORD="mypassword"

# %% [markdown]
### Modern way: Using the picas exec cli

# %%
# you will be prompted for the password
! picas-cli init --host-url https://picas.surfsara.nl:6984 --database mydatabase --username myusername

# %%
# you can also specify the password on the command line, but it is not recommended
! picas-cli init --host-url https://picas.surfsara.nl:6984 --database mydatabase --username myusername --password mypassword


# %% [markdown]
## Change the picas couchdb password
# To change the password, direct interaction with the CouchDB server can be used using the couchDB
# rest API, or the picas exec cli can be used.

### Changing the password using the couchDB rest API
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

# %%
!username=USERNAME
!password=PASSWORD
!newpassword=NEWPASSWORD
!curl --silent --user "$username:$password" -X GET https://picas.surfsara.nl:6984/_users/org.couchdb.user:$username | jq '._rev' |  curl --user "$username:$password" -X PUT https://picas.surfsara.nl:6984/_users/org.couchdb.user:$username -H "Accept: application/json" -H "Content-Type: application/json" -H "If-Match:$(</dev/stdin)" -d '{"name":"'$username'", "roles":[], "type":"user", "password":"'$newpassword'"}'


### Changing the password using the picas exec cli
# The picas exec cli can be used to change the password, which is more convenient.
# The password is encrypted and stored in the configuration file.
# %%! picas passwd

# %%
# the password can also be specified on the command line, but it is not recommended
! picas-cli passwd --password mynewpassword

# %% [markdown]
### Create the DB views

# %%
%cd examples
!python create_views.py
# %%
