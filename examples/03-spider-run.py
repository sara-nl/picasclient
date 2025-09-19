# %% [markdown]

## Use PiCaS to run tasks on Spider

### Outline
# - Set up a non trivial example - count the number of words in text files
# - Create tokens and push them to the database
# - Run the tasks on Spider using PiCaS by pulling tokens from the database

### references
# - 02-local-run.ipynb notebook

### Minimum requirements
# - you have run the 02-local-run.ipynb notebook and have a working PiCaS database
# - you have access to Spider (works also on Snellius but you need to update the slurm script)

# %%
%cd ~/picas_tutorial/picasclient/examples
! ls

# %% [markdown]
### Generate some fake data

# %%
! pip install faker tqdm

# %%
import os
import random
import re
from pathlib import Path
from faker import Faker
from tqdm import tqdm

# %%

data_dir = "~/picas_tutorial/picas_fake_data"

# %%
data_dir = os.path.expanduser(data_dir)
# ---------------------- CONFIG ----------------------
ROOT_DIR = Path(os.path.expanduser(data_dir))
SEED = None  # set to an int for reproducibility, e.g., 42

TOP_LEVEL_COUNTRIES = 5
MAX_CITIES_PER_COUNTRY = 5
MAX_FIRSTNAMES_PER_CITY = 5
MAX_LASTNAMES_PER_FIRSTNAME = 5

FILES_PER_LEAF = 10          # set up to 100 if desired
MIN_WORDS_PER_FILE = 10
MAX_WORDS_PER_FILE = 1000
# ----------------------------------------------------

if SEED is not None:
    random.seed(SEED)

# Faker instances: English names for people, general for places
fake_global = Faker()
fake_en = Faker("en_US")
if SEED is not None:
    fake_global.seed_instance(SEED)
    fake_en.seed_instance(SEED + 1 if isinstance(SEED, int) else None)

def sanitize(name: str) -> str:
    """Make a filesystem-safe folder/file name."""
    name = name.strip()
    name = re.sub(r"[\/\\:*?\"<>|]", "", name)  # remove reserved characters
    name = re.sub(r"\s+", "_", name)
    return name or "unnamed"

def unique_items(generator, count):
    """Return up to 'count' unique items from a callable generator()."""
    seen = set()
    items = []
    attempts = 0
    while len(items) < count and attempts < count * 20:
        attempts += 1
        val = generator()
        if val not in seen:
            seen.add(val)
            items.append(val)
    return items

def gen_words(n: int) -> str:
    """Generate n 'readable' lorem-like words with occasional punctuation."""
    words = fake_global.words(nb=n)
    out = []
    counter = 0
    break_at = random.randint(12, 20)
    for w in words:
        out.append(w)
        counter += 1
        if counter >= break_at:
            out[-1] = out[-1] + "."
            counter = 0
            break_at = random.randint(12, 20)
    text = " ".join(out)
    text = ". ".join(s.strip().capitalize() for s in text.split(".") if s.strip())
    if not text.endswith("."):
        text += "."
    return text

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def generate_data():
    ensure_dir(ROOT_DIR)

    # Pre-calculate the directory structure
    structure = []
    total_files = 0

    countries = unique_items(lambda: sanitize(fake_global.country()), TOP_LEVEL_COUNTRIES)

    for country in countries:
        country_dir = ROOT_DIR / country
        num_cities = random.randint(1, MAX_CITIES_PER_COUNTRY)
        cities = unique_items(lambda: sanitize(fake_global.city()), num_cities)

        for city in cities:
            city_dir = country_dir / city
            num_first = random.randint(1, MAX_FIRSTNAMES_PER_CITY)
            first_names = unique_items(lambda: sanitize(fake_en.first_name()), num_first)

            for first_name in first_names:
                first_dir = city_dir / first_name
                num_last = random.randint(1, MAX_LASTNAMES_PER_FIRSTNAME)
                last_names = unique_items(lambda: sanitize(fake_en.last_name()), num_last)

                for last_name in last_names:
                    leaf_dir = first_dir / last_name
                    structure.append(leaf_dir)
                    total_files += FILES_PER_LEAF

    print(f"Generating {total_files} files in {len(structure)} directories...")

    # Create all directories and files with a single progress bar
    with tqdm(total=total_files, desc="Creating files", unit="file") as pbar:
        for leaf_dir in structure:
            ensure_dir(leaf_dir)

            for i in range(1, FILES_PER_LEAF + 1):
                fname = f"file_{i:03d}.txt"
                fpath = leaf_dir / fname
                word_count = random.randint(MIN_WORDS_PER_FILE, MAX_WORDS_PER_FILE)
                content = gen_words(word_count)
                fpath.write_text(content, encoding="utf-8")
                pbar.update(1)

    print(f"\n✅ Done. Created {total_files} files in structure under: {ROOT_DIR.resolve()}")

# %%
generate_data()

# %%
# check the generated data

# %%
# examine the dir structure
! tree -L 2 {data_dir}

# %%
# examine some files
! find {data_dir} | head -20

# %% [markdown]
### Create and push tokens to the database

#### Traverse the directory structure and create tokens

# %%
import glob
token_inputs = [fpath for fpath in glob.iglob(f"{data_dir}/**/*.txt", recursive=True)]

# %%
# print some of the paths
from pprint import pprint
fields = {"input": token_inputs}
pprint(fields["input"][:10])  # print first 10 paths

# %% [markdown]
# push the tokens to the database

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


# %%
from create_tokens import create_tokens
from time import perf_counter
tokens = create_tokens(fields, offset=db.doc_count())
pprint(tokens[:10])

# %% [markdown]
# The push tokens script (save them to the database)

# %%
from time import perf_counter
start = perf_counter()
status = db.save_documents(tokens)
elapsed = perf_counter() - start

# %%
rate = len(tokens) / elapsed
print(f"Pushed {len(tokens)} in {elapsed:.3f}s ({rate:.1f} tokens/s)")

# %%
# get the number of documents in the todo view
print(f"Number of documents in the todo view: {db.db.view('Monitor/todo').total_rows}")

# %% [markdown]
# submit the job on spider to process all the tokens and do a word count on all the file
! sbatch spider_example_word_count.sh

# %% [markdown]
# - navigate to the database web UI
# - check the done view
# - click on a token  and check the attachments (word_count)

# %% [markdown]
### Detailes of the example script

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
