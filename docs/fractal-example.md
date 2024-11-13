PiCaS fractal example in Grid
============



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

