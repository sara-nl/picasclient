picasclient
-----------

![CICD](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg) [![License - MIT](https://img.shields.io/github/license/sara-nl/picasclient)](https://github.com/sara-nl/picasclient/blob/main/LICENSE)

Python client using CouchDB as a token pool server.

Installation
============

To install, first clone the repository and then use pip to install:
```
git clone https://github.com/sara-nl/picasclient.git
cd picasclient
pip install -U .
```

If you come across error messages related to python, you can execute pip module for a specific python version using the corresponding python:
```
python3.9 -m  pip install -U .
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

The examples directory contains examples to use the picasclient. There are examples for running locally (laptop, cluster login), to a slurm job scheduler and the Grid (https://www.egi.eu/), and in principle the jobs can be sent to any machine that can run this client.

To run the examples, first you need to have a CouchDB instance running that functions as the token broker that stores the tokens which the worker machines can approach to get work execute. To set up this CouchDB instance, see the [SURF documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_overview.html#picas-server-1), these examples assume you have an instance running and access to a DB on this instance. If you are following a workshop organized by SURF, this has already been arranged for you.

Once this server is running, you can run the PiCaS examples:
 - Local
 - Slurm
 - Grid


## Prepare the tokens


To approach the DB, you have to fill in the `examples/picasconfig.py` with the information to log in to your CouchDB instance and the database you want use for storing the work tokens. Specifically, the information needed are:
```
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE=""
PICAS_USERNAME=""
PICAS_PASSWORD=""
```
### Create views
Once you can approach the server, you have to define "view" logic, so that you can easily view large numbers of tokens and filter on new, running and finished tokens. To create these views, run:

```
python createViews.py
```

### Create tokens
This example includes a bash script `(./createTokens)` that generates a sensible parameter file, with each line representing a set of parameters that the fractals program can be called with. Without arguments it creates a fairly sensible set of 24 lines of parameters. You can generate different sets of parameters by calling the program with a combination of `-q`, `-d` and `-m` arguments, but at the moment no documentation exists on these. We recommend not to use them for the moment.
```
./createTokens
```
After you ran the `createTokens` script you’ll see output similar to the following:
```
/tmp/tmp.fZ33Kd8wXK
cat /tmp/tmp.fZ33Kd8wXK
```

### Upload tokens to the PiCaS server


Next you have to send some tokens containing work to the CouchDB instance. You can send two types of work in this example. For very fast running jobs, send the `quickExample.txt` file with:
```
python pushTokens.py quickExample.txt
```

For longer jobs example with a set of 24 lines of parameters. send the file generated in the create tokens step:
```
python pushTokens.py /tmp/tmp.fZ33Kd8wXK
```

### Reset tokens 

### Delete tokens

To delete all the Tokens in a certain view, you can use the `deteleTokens.py` under the `examples` directory. For example to delete all the tokens in todo view, run
```
python /path-to-script/deleteTokens.py Monitor/todo
```



Now we are ready to run the examples! You can start with running a quick example on different systems. Or you can jump to "Running the long jobs" section for a more complex example.

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

In this fractal example we will implement the following pilot job workflow:

* First we define and generate the application tokens with all the necessary parameters.
* Then we define and create a shell script to process one task (*process_task.sh*) that will be sent with the job using the input sandbox. This contains some boiler plate code to e.g. setup the environment, download software or data from the Grid storage, run the application etc. This doesn’t have to be a shell script, however, setting up environment variables is easiest when using a shell script, and this way setup scripts are separated from the application code.
* We also define and create a Python script to handle all the communication with the token pool server, call the process_task,sh script, catch errors and do the reporting.
* Finally we define the :abbr:`JDL (Job Description Language)` on the User Interface machine to specify some general properties of our jobs. This is required to submit a batch of pilot jobs to the Grid that will in turn initiate the Python script as defined in the previous step.


### Prerequisites

To be able to run the example you must have:

* All the three Grid :ref:`prerequisites` (User Interface machine, Grid certificate, VO membership)
* An account on PiCaS server (send your request to <helpdesk@surfsara.nl>)



### Picas sample example


* Log in to the :abbr:`UI (User Interface)` and download the :download:`pilot_picas_fractals.tgz </Scripts/picas-python3/pilot_picas_fractals.tgz>` example, the couchdb package for Python :download:`couchdb.tgz </Scripts/couchdb.tgz>` and the fractals source code :download:`fractals.c </Scripts/fractals.c>`.

* Untar ``pilot_picas_fractals.tgz`` and inspect the content:

```
tar -xvf pilot_picas_fractals.tgz
cd pilot_picas_fractals/
ls -l
-rwxrwxr-x 1 homer homer 1247 Jan 28 15:40 createTokens
-rw-rw-r-- 1 homer homer 1202 Jan 28 15:40 createTokens.py
-rw-rw-r-- 1 homer homer 2827 Jan 28 15:40 createViews.py
-rw-rw-r-- 1 homer homer  462 Jan 28 15:40 fractals.jdl
drwxrwxr-x 2 homer homer  116 Jan 28 15:40 sandbox
```

Detailed information regarding the operations performed in each of the scripts below is embedded to the comments inside each of the scripts individually.

* Also download the current PiCaS version :download:`picas.tar </Scripts/picas-python3/picas.tar>` and put both PiCaS and the couchdb.tgz file in the ``sandbox`` directory:

```
cd sandbox
mv ../../couchdb.tgz ./
mv ../../picas.tar ./
```

* And finally compile the fractals program (and put it in the sandbox directory) and move one directory up again:
```
cc ../../fractals.c -o fractals -lm
cd ..
```

The sandbox directory now holds everything we need to send to the Grid worker nodes.

Create the Tokens

This example includes a bash script (``./createTokens``) that generates a sensible parameter file, with each line representing a set of parameters that the fractals program can be called with. Without arguments it creates a fairly sensible set of 24 lines of parameters. You can generate different sets of parameters by calling the program with a combination of ``-q``, ``-d`` and ``-m`` arguments, but at the moment no documentation exists on these. We recommend not to use them for the moment.

* After you ran the ``createTokens`` script you'll see output similar to the following:
```
./createTokens
/tmp/tmp.fZ33Kd8wXK
cat /tmp/tmp.fZ33Kd8wXK
```
Now we will start using PiCaS. For this we need the downloaded CouchDB and PiCaS packages for Python and set the hostname, database name and our credentials for the CouchDB server:

* Edit ``sandbox/picasconfig.py`` and set the PiCaS host URL, database name, username and password.

```
ln -s sandbox/picasconfig.py
```

* Make the CouchDB package locally available:
```
tar -xvf sandbox/couchdb.tgz
```

* Upload the tokens:

```
$python createTokens.py /tmp/tmp.fZ33Kd8wXK
```

* Check your database in this link:
```
https://picas.surfsara.nl:6984/_utils/#/database/homerdb/_all_docs (replace homerdb with your Picas database name)
```

* Create the Views (pools) - independent to the tokens (should be created only once):

```
python createViews.py
```
To make use of the dirac tool, first source the dirac env

```
source /etc/diracosrc
```

* Create a proxy:
```
dirac-proxy-init -b 2048 -g lsgrid_user -M lsgrid --valid 168:00 # replace lsgrid with your VO
```

* Submit the pilot jobs:
```
dirac-wms-job-submit fractals.jdl -f jobIDs
```


It will recursively generate an image based on parameters received from PiCas. At this point, some of your tokens are processed on the Grid worker nodes and some of the tokens are already processed on the :abbr:`UI (User Interface)`. Note that the :abbr:`UI (User Interface)` is not meant for production runs, but only for testing few runs before submitting the pilot jobs to the Grid.

* Convert the :abbr:`UI (User Interface)` output file to .png format and display the picture:
```
convert output_token_6 output_token_6.png # replace with your output filename
```

For the tokens that are processed on Grid, you can send the output to the :ref:`Grid Storage <grid-storage>` or some other remote location.

As we have seen, through PiCaS you have a single interface that can store tokens with work to be done (the CouchDB instance). Then on any machine where you can deploy the PiCaS client, one can perform the tasks hand.


## Running the long jobs

The example above is very fast in running (it only echos to your shell). To get an idea on longer running jobs there is also a "fractal" example. 
The work in this example takes from 10 seconds up to 30 minutes per token. To add these tokens to your DB, do:

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
mkdir bin
cc src/fractals.c -o bin/fractals -lm
```

And finally, the `process_task.sh` code needs to call a different command. Replace

```
eval $INPUT
```

with:

```
cd bin
./fractals -o $OUTPUT $INPUT
```

to ensure the fractal code is called.

Now, you can run your jobs whichever way you want (locally, slurm, grid) and start submitting job!

It will recursively generate an image based on parameters received from PiCas. Once the jobs are run successfully, you can find the output in the bin directory. 
Convert the output file to .png format and display the picture: 
```
convert output_token_6 output_token_6.png # replace with your output filename
display output_token_6.png
```

## Checking failed jobs

While your pilot jobs process tasks, you can keep track of their progress through the CouchDB web interface. There are views installed to see:

 * all the tasks that still need to be done (Monitor/todo)
 * the tasks that are locked (Monitor/locked)
 * tasks that encountered errors (Monitor/error)
 * tasks that are finished (Monitor/done)

When all your pilot jobs are finished, ideally, you'd want all tasks to be 'done'. However, often you will find that not all jobs finished successfully and some are still in a 'locked' or 'error' state. If this happens, you should investigate what went wrong with these jobs. Incidentally, this will be due to errors with the middleware, network or storage. In those cases, you can remove the locks and submitting some new pilot jobs to try again. In other cases, there could be errors with your task: maybe you've sent the wrong parameters or forgot to download all necessary input files. Reviewing these failed tasks gives you the possibility to correct them and improve your submission scripts. After that, you could run those tasks again, either by removing their locks or by creating new tokens if needed and then submitting new pilot jobs.

Picas overview
==============

Here is an overview of the layers in picas and how they relate to the code in the `examples` folder.

![picas layers](./docs/picas-layers.png)
