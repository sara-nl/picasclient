# %% [markdown]

## Setup and connect to the Picas database

### references
# - the official picas client repository: https://github.com/sara-nl/picasclient
# - the main couchdb database: https://picas.surfsara.nl:6984
# - the couchdb web ui login page: https://picas.grid.sara.nl:6984/_utils/#login
# - picas spider workflows: https://doc.spider.surfsara.nl/en/latest/Pages/workflows.html#picas
# - more documentation: https://doc.grid.surfsara.nl/en/latest/
# - change the picas couchdb password: https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_change_password.html

### Minimum requirements
# Make sure that the 00-environment-setup notebook has been run and that the virtual environment is activated.
# cd ~/workspaces/surf/picas/picasclient
# source .venv/picas-tutorial/bin/activate
# pip install notebook
# python setup.py install
# pip install -e .   # not sure why this is not installed the picas exec cli script
# jupyter notebook --no-browser
