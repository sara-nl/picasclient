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
%cd ~/picas_tutorial
! ls

# %% [markdown]
### Generate some fake data

# %%
! pip install faker tqdm

# %%
import random
import re
from pathlib import Path
from faker import Faker
from tqdm import tqdm

# %%
# ---------------------- CONFIG ----------------------
ROOT_DIR = Path("/dev/shm/picas_fake_data")  # create data in shared memory for faster access
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

# %% [markdown]
### CONTINUE FROM HERE
# - create and push the tokens in python
# - modify the process_task.sh to execute the word count python script (create it)
# - create the process_text_file.py that does something to the text files (e.g. count words, or summarization)
# - add option to summarize the text file content ( separate heading - prioritize the word count)
# - add the script to submit to slurm on spider (spider_example.sh)
# - submit the job
# - wait for all to finish
# - fetch the results from the db and visualize them (word count histogram)
# - for the summaization maybe only do a sentiment analysis and show a histogram of that