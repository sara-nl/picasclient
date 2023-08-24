picasclient
-----------

![CICD](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg)

Python client using CouchDB as a token pool server.

Installation
============

To install run
```
pip install -U .
```

Testing
=======

First, install the test dependencies with 
```
pip install ".[test]"
```
To test, run
```
flake8 picas tests
pytest tests
```

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

To do more work, you will have to add new tokens that are not in a "done" state yet, otherwise the example script will just stop after finding no work to do.

## Running on Slurm

To run on slurm, first open the `slurm-example.sh` file and make sure your python virtual env or conda/mamba environment is loaded.
Then you have to add tokens to CouchDB using the same setup procedure as mentioned above, with the pushTokens script.

To start the slurm job that runs the PiCaS client do:

```
sbatch slurm-example.sh
```

Now in a slurm job array (you can set the number of array jobs in the script at `--array`) and each job will start polling the CouchDB instance for work. Once the work is complete, the jobs will finish.

## Running on Grid

On the grid, in our screnario, you need to supply the entire environment through the sandbox (the alternative CVMFS goes beyond the scope of these examples). The binaries and python code need to be in this sandbox.
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
dirac-wms-job-submit fractals.jdl
```

And the status and output can be retrieved with the usual DIRAC commands, while in the token you see the status of the token and the tokens' attachments contain the log files.

As we have seen, through PiCaS you have a single interface that can store tokens with work to be done (the CouchDB instance). Then on any machine where you can deploy the PiCaS client, one can perform the tasks hand.

## Running the long jobs

To send longer running code (it takes from 10 seconds up to 30 minutes per token), do:

```
./createTokens
>>> /tmp/tmp.abc123
```

And pass the output file to the push tokens code:

```
python pushTokens.py /tmp/tmp.abc123
```

Now the tokens are available in the database. Next, the binary for the calculation needs to be built:

```
cc src/fractals.c -o bin/fractals -lm
```

And finally, the `process_task.sh` code needs to call a different command. Replace

```
eval $INPUT
```

with:

```
./fractals -o $OUTPUT $INPUT
```

to ensure the fractal code is called.

Now, you can run your jobs whichever way you want (locally, slurm, grid) and start running using the general instructions as described above!



## QuantifiedCode Automated code review  

[![Code Issues](https://www.quantifiedcode.com/api/v1/project/b54df6dfb35b4325b6104fb854a1f141/badge.svg)](https://www.quantifiedcode.com/app/project/b54df6dfb35b4325b6104fb854a1f141)
