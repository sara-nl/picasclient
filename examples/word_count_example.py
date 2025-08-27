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
# Process the tokens by pulling tokens and using the PiCaS framework to run the tasks locally
# in each job on Spider

# %%
from picas.actors import RunActor
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
    def __init__(self, db, modifier, view="todo", **viewargs):
        super(ExampleActor, self).__init__(db, view=view, **viewargs)
        self.timer = Timer()
        self.modifier = modifier
        self.client = db

    def process_task(self, token):
        # Print token information
        print("-----------------------")
        print("Working on token: " + token['_id'])
        for key, value in token.doc.items():
            print(key, value)
        print("-----------------------")

        data_fpath = token['input']

        with open(data_fpath, 'r') as fobj:
            text = fobj.read()
            word_count = len(text.split())

        self.subprocess = None

        ## Get the job exit code and done in the token (since counting words is trivial)
        ## assume it has succeeded
        token['exit_code'] = 0
        token = self.modifier.close(token)

        ## Attach the word count
        token.put_attachment('word_count', f'{word_count}\n')


# %%
# create the token modifier
modifier = BasicTokenModifier()

# %%
# create the actor
actor = ExampleActor(db, modifier, view='todo', design_doc='Monitor')

# %%
# start the work!
actor.run(max_token_time=1800, max_total_time=3600, max_tasks=100000, max_scrub=2)

# %% [markdown]
# - navigate to the database web UI
# - check the done view
# - click on a token  and check the attachments (word_count)
