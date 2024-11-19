picasclient
-----------

![CICD](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg) [![License - MIT](https://img.shields.io/github/license/sara-nl/picasclient)](https://github.com/sara-nl/picasclient/blob/main/LICENSE)

Python client using CouchDB as a token pool server.

Installation
============

Development & Testing
---------------------

To install `picas` source code for development, first clone the repository and then use [`poetry`](https://python-poetry.org/docs/) to install. `poetry` is a tool for dependency managing and packaging in Python. If you don't have `poetry`, install it first with `pipx install poetry`.
```
git clone git@github.com:sara-nl/picasclient.git
cd picasclient
poetry install --with test
```
Note that poetry will create a virtual environment if it is not running within an activated virtual environment already. In that case, you will need to run `poetry run` before your commands to execute them within the poetry virtual environment.

If you prefer not to use `poetry`, then you can install with (in a virtual environment):
```
pip install -U .
pip install flake8 pytest
```

To test, run
```
flake8 picas tests
pytest tests
```

Installing package
------------------
The latest release of `picas` can be installed as a package from PyPI with:
```
pip install picas
```
You can then write your custom Python program to use `picas` based on the examples below. 



Examples
========

## Setting up the examples

The examples directory contains examples to use the picasclient. There are examples for running locally (laptop, cluster login), slurm and the Grid (https://www.egi.eu/), and in principle the jobs can be sent to any machine that can run this client.

To run the examples, first you need to have a CouchDB instance running that functions as the token broker that stores the tokens which the worker machines can approach to get work execute. To set up this CouchDB instance, see the [SURF documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_overview.html#picas-server-1), these examples assume you have an instance running and access to a DB on this instance.

Once this server is running, you can run the PiCaS examples:
 - Local
 - Slurm
 - Grid

To approach the DB, you have to fill in the `examples/picasconfig.py` with the information to log in to your CouchDB instance and the database you want use for storing the work tokens.

Once you can approach the server, you have to define "view" logic, so that you can easily view large numbers of tokens and filter on new, running and finished tokens. To create these views, run:

```
python createViews.py
```

Next you have to send some tokens containing work to the CouchDB instance. You can send two types of work in this example. For very fast running jobs, send the `quickExample.txt` file with:

```
python pushTokens.py quickExample.txt
```

Now we are ready to run the examples!

## Running locally

To run the local example do:

```
python local-example.py
```

If all goes well you should see output like:

```
-----------------------
Working on token: token_0
_id token_0
_rev 4-8b04da64c0a536bb88a3cdebe12e0a87
type token
lock 1692692693
done 0
hostname ui-01.spider.surfsara.nl
scrub_count 0
input echo "bash-echo"
exit_code 0
-----------------------
```

The token in de database will have attachments with the regular and error output of the terminal. There will find the output file `logs_token_0.out`, containing the output of the input command:

```
echo "bash-echo"
>>> bash-echo
```

Once the script is running, it will start polling the CouchDB instance for work. Once the work is complete, the script will finish.

Tokens have a status, that will go from "todo" to "done" once the work has been completed (or "failed" if the work fails). To do more work, you will have to add new tokens that are not in a "done" state yet, otherwise the example script will just stop after finding no work to do.

## Running on Slurm

To run on slurm, first open the `slurm-example.sh` file and make sure your python virtual env or conda/mamba environment is loaded.
Then you have to add tokens to CouchDB using the same setup procedure as mentioned above, with the pushTokens script.

To start the slurm job that runs the PiCaS client do:

```
sbatch slurm-example.sh
```

Now in a slurm job array the work will be performed (you can set the number of array jobs in the script at `--array`) and each job will start polling the CouchDB instance for work. Once the work is complete, the jobs will finish.

## Running on Grid

### Fractal example

On the grid, in our screnario, you need to supply the entire environment through the sandbox (a more grid-native CVMFS example is available in the [picas-profile](https://github.com/sara-nl/picas-profile) repository). The binaries and python code need to be in this sandbox.
First we need to create a tar of the picas code, so that it can be sent to the Grid:

```
tar cfv grid-sandbox/picas.tar ../picas/
```

Secondly, the CouchDB python API needs to be available too, so download and extract it:

```
wget https://files.pythonhosted.org/packages/7c/c8/f94a107eca0c178e5d74c705dad1a5205c0f580840bd1b155cd8a258cb7c/CouchDB-1.2.tar.gz
```

Now you can start the example from a grid login node with (in this case DIRAC is used for job submission):

```
dirac-wms-job-submit grid-example.jdl
```

And the status and output can be retrieved with DIRAC commands, while in the token you see the status of the token and the tokens' attachments contain the log files. Once all tokens have been processed (this can be seen in the CouchDB instance) the grid job will finish.

As we have seen, through PiCaS you have a single interface that can store tokens with work to be done (the CouchDB instance). Then on any machine where you can deploy the PiCaS client, one can perform the tasks hand.


## Running the long jobs

The example above is very fast in running (it only echos to your shell). To get an idea on longer running jobs there is also a "fractal" example. The work in this example takes from 10 seconds up to 30 minutes per token. To add these tokens to your DB, do:

```
./createTokens
>>> /tmp/tmp.abc123
```

And pass the output file to the push tokens code:

```
python pushTokens.py /tmp/tmp.abc123
```

Now the tokens are available in the database. Next, the binary for the fractal calculation needs to be built:

```
cc src/fractals.c -o bin/fractals -lm
```

And finally, the `process_task.sh` code needs to call a different command. Replace

```
bash -c "$INPUT"
```

with:

```
bin/fractals -o $OUTPUT $INPUT
```

to ensure the fractal code is called.

Now, you can run your jobs whichever way you want (locally, slurm, grid) and start running using the general instructions as described above!


Picas overview
==============

Here is an overview of the layers in picas and how they relate to the code in the `examples` folder.

![picas layers](./docs/picas-layers.png)
