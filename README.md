picasclient
-----------

![CICD](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg) [![License - MIT](https://img.shields.io/github/license/sara-nl/picasclient)](https://github.com/sara-nl/picasclient/blob/main/LICENSE)

Python client using [CouchDB](https://docs.couchdb.org/en/stable/index.html) as a token pool server (PiCaS).


Installation
============

Development & Testing
---------------------

To install the PiCaS source code for development, first clone this repository and then use [`poetry`](https://python-poetry.org/docs/) to install. Poetry is a tool for dependency managing and packaging in Python. If you don't have Poetry, install it first with `pipx install poetry`.
```
git clone https://github.com/sara-nl/picasclient.git
cd picasclient
poetry install --with test
```
Note that Poetry will create a virtual environment if it is not running within an activated virtual environment already. In that case, you will need to run `poetry run` before your commands to execute them within the Poetry virtual environment.

If you prefer not to use Poetry, then you can install PiCaS with:
```
pip install -U .
pip install flake8 pytest
```

To test, run:
```
flake8 picas tests
pytest tests
```


Installing package
------------------
Alternatively, the latest release of PiCaS can be installed as a package from PyPI with:
```
pip install picas
```
You can then write your custom Python program to use PiCaS as a library based on the examples below. 


Examples
========

The `examples` directory contains two examples how to use the PiCaS client: a short example and a long example. These also include scripts for running locally, on [Spider](https://doc.spider.surfsara.nl/en/latest/Pages/about.html) (SLURM cluster) and the [Grid](https://doc.grid.surfsara.nl/en/latest/). The examples will show how PiCaS provides a single interface that can store tokens (on the CouchDB instance) with work to be done. Then jobs can be sent to any machine where the PiCaS client can be deployed.

Prerequisites
-------------

<details closed>
<summary>Get a PiCaS account</summary>
<br>

To run the examples, you need a PiCaS account and access to a database (DB) on the PiCaS CouchDB instance. If you are following a workshop organized by SURF, this has already been arranged for you. If you have a Grid or Spider project at SURF, you can request access through the <a href="https://servicedesk.surf.nl">Service Desk</a>
</details>


<details closed>
<summary>Connect to the PiCaS server</summary>
<br>

To connect to the PiCaS server, fill `examples/picasconfig.py` with the information needed to log in to your PiCaS account and the database you want to use for storing the work tokens. Specifically, the information needed are:
  
```
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE=""
PICAS_USERNAME=""
PICAS_PASSWORD=""
```
</details>


<details closed>
<summary>Create DB Views</summary>
<br>

When you you use the DB for the first time, you need to define "view" logic and create views. <a href="https://docs.couchdb.org/en/stable/ddocs/views/index.html">CouchDB Views</a> are the primary tool used for querying and reporting on CouchDB documents. For example, you can create views to filter on new, running, finished, and failed job tokens. Some pre-defined views can be created with:

```
cd examples
python createViews.py
```
This will create the following views:
 * `Monitor/todo`: tasks that still need to be done
 *` Monitor/locked`: tasks that are currently running
 * `Monitor/error`: tasks that encountered errors 
 * `Monitor/done`: tasks that are finished 
 * `Monitor/overview_total`: all tasks and their states
   
After a few moments, you should be able to find the generated views in the <a href="https://picas.surfsara.nl:6984/_utils/#login">CouchDB web interface</a>. Select your database and you will see the views on the left under `Monitor/Views`:

![picas views](docs/picas-views.png)
</details>


Quick example
-------------
This example creates fast-running jobs that write a message to standard output.
<details closed>
<summary>Create tokens</summary>
<br>

The file `quickExample.txt` contains three lines with commands to be executed. You can generate three job tokens in the PiCaS DB by running: 

```
python pushTokens.py quickExample.txt
```

Check the DB; you should see the tokens in the view `Monitor/todo`. 
</details>


<details closed>
<summary>Running locally</summary>
<br>

To run the example locally (e.g. on your laptop) with:

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
hostname xxxxxxxxxxxx
scrub_count 0
input echo "this is token A"
exit_code 0
-----------------------
```

The token in the database will have attachments with the standard and error output of the terminal. There you will find the outputfile `logs_token_0.out`, containing the output of the input command:

```
Tue 31 Dec 2024 00:00:00 CET
xxxxxxxxxxxx
echo 'this is token A'
token_0
output_token_0
this is token A
Tue 31 Dec 2024 00:00:00  CET
```

Once the script is running, it will start polling the Picas server for work. Once the work is complete, the script will finish.

Tokens have a status, which will go from "todo" to "done" once the work has been completed (or "failed" if the work fails). To do more work, you will have to add new tokens that in the "todo" state yet, otherwise the example script will just stop after finding no more work to do. If you are interested, you can look into the scripts `examples/local-example.py` and `examples/process_task.sh` to check what the actual work is.
</details>


<details closed>
<summary>Running on a cluster with SLURM</summary>
<br>

To start the SLURM job which runs the PiCaS client, run the `slurm-example.sh` from the `examples` directory:

```
sbatch slurm-example.sh
```

Now in a SLURM job array the work will be performed (you can set the number of array jobs in the script at `--array`) and each job will start polling the CouchDB instance for work. Once the work is complete, the SLURM job will finish.
</details>


<details closed>
<summary>Running on the Grid with DIRAC</summary>
<br>

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

And the status and output can be retrieved with DIRAC commands, while in the token you see the status of the token and the tokens' attachments contain the log files. Once all tokens have been processed (check the DB Views) the grid job will finish.
</details>


<details closed>
<summary>Check results</summary>
<br>

While your pilot jobs process tasks, you can keep track of their progress through the CouchDB web interface and the views we created earlier. 

When all pilot jobs are finished, ideally, you want all tasks to be "done". However, often you will find that not all jobs finished successfully and some are still in a "locked" or "error" state. If this happens, you should investigate what went wrong with these jobs. Incidentally, this might be due to errors with the middleware, network or storage. In those cases, you can remove the locks and submit new pilot jobs to try again. 

In other cases, there could be errors with your task: maybe you've sent the wrong parameters or forgot to download all necessary input files. Reviewing these failed tasks gives you the possibility to correct them and improve your submission scripts. After that, you could run those tasks again, either by removing their locks or delete older tokens and creating new tokens. After that, you can submit new pilot jobs.

To delete all the tokens in a certain view, you can use the script `deteleTokens.py`. For example to delete all the tokens in "error" view, run:

```
python deleteTokens.py Monitor/error
```
</details>


Long example: fractals
----------------------
To get an idea on more realistic, longer running jobs there is also a "fractals" example. The fractals code will recursively generate an image based on parameters received from PiCas. The work can take from 10 seconds up to 30 minutes per token.


<details closed>
<summary>Create tokens</summary>
<br>
To add the fractals job tokens to your DB, run:

```
./createTokens
>>> /tmp/tmp.abc123
```
This will generate an outputfile, in this case called `/tmp/tmp.abc123`. Pass the outputfile to the `pushTokens.py` code:

```
python pushTokens.py /tmp/tmp.abc123
```
Now the tokens are available in the database. 
</details>


<details closed>
<summary>Prepare code</summary>
<br>
Next, the binary for the fractal calculation needs to be built:
  
```
cc src/fractals.c -o bin/fractals -lm
```

And finally, the `process_task.sh` code needs to call a different command. Replace:

```
bash -c "$INPUT"
```
with:

```
bin/fractals -o $OUTPUT $INPUT
```
to ensure that the fractals code is called.
</details>


<details closed>
<summary>Run jobs locally, SLURM cluster or Grid</summary>
<br>

Now, you can run your jobs whichever way you want (locally, SLURM cluster or the Grid), using the general instructions as described above for the quick example!
</details>


<details closed>
<summary>Check results</summary>
<br>

The fractals code will generate an outputfile named `output_token_X`. If the jobs are run locally or on Spider, you can find the outputfile in your work directory. For jobs that are processed on the Grid, you can transfer the outputfile to a remote storage location at the end of your job script `process_task.sh`. To check the results, convert the output file to .png format and display the picture: 
  
```
convert output_token_6 output_token_6.png # replace with your output filename
display output_token_6.png
```
</details>


PiCaS overview
==============

Below is an overview of the layers in PiCaS and how they relate to the code in the `examples` folder. The scripts `slurm-example.sh` and `grid-example.jdl` are for scheduling jobs on a SLURM cluster and the Grid, respectively. For the Grid, there is an extra script `startpilot.sh` needed to start the job on the GRID Computing Environment. Finally, a job is run with `local-example.py` in the same way when tokens are processed locally.

![picas layers](./docs/picas-layers.png)