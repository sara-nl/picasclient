PiCaS quick example
============

To demonstrate how pilot job PiCaS works, this page gives instructions on running a quick example which takes probably a few minutes. The quick example including four main steps: 
  1. connect to Picas server
  2. prepare and upload tokens to Picas server
  3. run Picas example pilot job
  4. check the tokens and results


## Prerequisite

Before running the example, please read the README.md in [Picas Client](https://github.com/sara-nl/picasclient/). The prerequisites are:
  * you have installed and tested the Picas client
  * you have a Picas account and a Picas database
  * there is a Picas token pool server running on CouchDB.

If you are following a workshop organized by SURF, the last two requirements have already been arranged for you.


## Connect to Picas server

To connect to the Picas server CouchDB, you need to fill in the `examples/picasconfig.py` with the information to log in to your Picas server and the database you want use for storing the work tokens. Specifically, the information needed are:
```
PICAS_HOST_URL="https://picas.surfsara.nl:6984"
PICAS_DATABASE=""
PICAS_USERNAME=""
PICAS_PASSWORD=""
```

Save and exit. Next don't forget to change the permissions of `examples/picasconfig.py`. Run:
```
cd examples
chmod 600 picasconfig.py
```

For the first time using Picas, you need to define "view" logic and create views. CouchDB views are the basic query mechanism in CouchDB and allow you to extract, transform and combine data from different documents stored in the same database.

To create these views, run:

```
python createViews.py
```
Once it is finished, you should be able to see the views in the [CouchDB web interface](https://picas.surfsara.nl:6984/_utils/#/database/database-name/). The link needs to be adjusted with your database name

## Prepare and upload tokens

Next you need to send some tokens containing work to the Picas server. For a quick example with fast running jobs, a `quickExample.txt` file is prepared containing three tokens. Run:
```
python pushTokens.py quickExample.txt
```

## Run Picas example

In principle, the pilot jobs can be sent to any machine that can run Picas client. For this Picas quick example, we provide instructions on running locally (laptop, cluster login), to a slurm job scheduler and the [Grid](https://www.egi.eu/).

### Running locally

To run the example locally, run from the `examples` directory:

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
hostname xxxxxxxxxxxxxxxxxxxxxxx
scrub_count 0
input echo "bash-echo"
exit_code 0
-----------------------
```

The token in the database will have attachments with the regular and error output of the terminal. There will find the output file `logs_token_0.out`, containing the output of the input command:

```
echo "bash-echo"
>>> bash-echo
```

Once the script is running, it will start polling the Picas server for work. Once the work is complete, the script will finish.

Tokens have status, which will go from "todo" to "done" once the work has been completed (or "failed" if the work fails). To do more work, you will have to add new tokens that are not in a "done" state yet, otherwise the example script will just stop after finding no more work to do.

### Running on a cluster with Slurm

To start the slurm job which runs the PiCaS client, run the `slurm-example.sh` from the `examples` directory:

```
sbatch slurm-example.sh
```

Now in a slurm job array the work will be performed (you can set the number of array jobs in the script at `--array`) and each job will start polling the CouchDB instance for work. Once the work is complete, the slurm job will finish.
If you are interested, you can look into scripts `examples/local-example.py` and `examples/process_task.sh` to check what the actual work is. 

### Running on the Grid

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


## Check the tokens and results

While your pilot jobs process tasks, you can keep track of their progress through the CouchDB web interface. There are views installed to see:

 * all the tasks that still need to be done (Monitor/todo)
 * the tasks that are locked (Monitor/locked)
 * tasks that encountered errors (Monitor/error)
 * tasks that are finished (Monitor/done)

When all your pilot jobs are finished, ideally you'd want all tasks to be 'done'. However, often you will find that not all jobs finished successfully and some are still in a 'locked' or 'error' state. If this happens, you should investigate what went wrong with these jobs. Incidentally, this might be due to errors with the middleware, network or storage. In those cases, you can remove the locks and submitting some new pilot jobs to try again. 

In other cases, there could be errors with your task: maybe you've sent the wrong parameters or forgot to download all necessary input files. Reviewing these failed tasks gives you the possibility to correct them and improve your submission scripts. After that, you could run those tasks again, either by removing their locks or delete older tokens and creating new tokens. After that, you can submit new pilot jobs.

To delete all the Tokens in a certain view, you can use the `deteleTokens.py` under the `examples` directory. For example to delete all the tokens in todo view, run
```
python /path-to-script/deleteTokens.py Monitor/todo
```

