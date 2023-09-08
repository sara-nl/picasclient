picasclient
-----------

![CICD](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg)

Python client using CouchDB as a token pool server.

Installation
============

To install, first clone the repository and then use pip to install:
```
git clone git@github.com:sara-nl/picasclient.git
cd picasclient
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

### Fractal example

On the grid, in our screnario, you need to supply the entire environment through the sandbox (the alternative CVMFS is used in the advanced grid example). The binaries and python code need to be in this sandbox.
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

### Advanced Grid example (snakemake)

To run the Snakemake turorial example on the grid using PiCaS, there are some prerequisites. It helps to be up to speed with the full tutorial, so read it [here](https://snakemake.readthedocs.io/en/stable/tutorial/tutorial.html).

First, setup the snakemake stack and profile as described above and in [the profile readme](https://github.com/sara-nl/picas-profile) on a Grid UI machine. Snakemake will be run from this machine, which then pushes the work to the CouchDB back-end. You can use the usual Snakefile from the tutorial for steering snakemake.
This work is subsequently pulled by a pilot job on the Grid, performed, and stored on Grid Storage.

Second, a CVMFS repository needs to be available for the snakemake calls that are done on the Grid Compute Element. To distribute the snakemake code, connect to a CVMFS distribution machine and create a new conda/mamba environment in `/cvmfs/path/to/your/space`.
For brevity, here are example steps for a simple snakemake environment that should have all the components needed to run on the Grid:

```
conda create -c conda-forge -c bioconda -n snakemake-picas snakemake
conda install -c bioconda samtools
conda install -c bioconda bcftools
conda install python-gfal2
```

Gfal2 is used for interacting with Grid Storage. Now publish the conda environment and wait until its available on CVMFS.

Next, set up the data needed for the snakemake example on your grid storage, see the tutorial linked at the top of this subsection.
The data will look something like this on your storage cluster:

```
rclone ls token:/path/to/snakemake/files/

   234112 data/genome.fa
     2598 data/genome.fa.amb
       83 data/genome.fa.ann
   230320 data/genome.fa.bwt
       18 data/genome.fa.fai
    57556 data/genome.fa.pac
   115160 data/genome.fa.sa
  5752788 data/samples/A.fastq
  5775000 data/samples/B.fastq
  5775000 data/samples/C.fastq
```

We will distribute the `plot-quals.py` to shortly show how the sandbox works. Also the Snakefile is needed in the sandbox, so creatae two links, one to each of the files:

```
cd /path/to/picasclient/
cd examples/grid-sandbox
ln -s  /path/to/snakemake/scripts/plot-quals.py plot-quals.py
ln -s  /path/to/snakemake/Snakefile Snakefile
```

To properly call `plot-quals.py` on the Grid, the Snakefile has to be updated. On the grid the `scripts` folder will not exist in the sandbox, as the files are placed in the root of the Grid machine. So remove the `scripts` from the Snakefile.

Now you need to do two things after one another to get Snakemake to run on the Grid:

1. Start a job on the grid running the picas client
2. Start snakemake using the picas profile installed before

```
cd /path/to/picasclient/examples
dirac-wms-job-submit snakemake.jdl
```

Now wait until this job is running. The picas client will wait for a time for jobs in the DB before quitting. If it times out too quickly, change the `time_elapsed` in `example/local-example.py` to something more managable (for example, 10 minutes).

Once the Grid job is running, start snakemake:

```
snakemake --profile picas -j 1
```

If all is set well, you will see the regular snakemake logging output in green. After the processing is finished, you will find the output files in your Grid storage:

```
rclone ls token:/path/to/snakemake/files/
  2183986 sorted_reads/A.bam
      344 sorted_reads/A.bam.bai
  2188317 sorted_reads/B.bam
      344 sorted_reads/B.bam.bai
  2200439 mapped_reads/A.bam
  2203496 mapped_reads/B.bam
    13008 plots/quals.svg
    69995 calls/all.vcf
   234112 data/genome.fa
     2598 data/genome.fa.amb
       83 data/genome.fa.ann
   230320 data/genome.fa.bwt
       18 data/genome.fa.fai
    57556 data/genome.fa.pac
   115160 data/genome.fa.sa
  5752788 data/samples/A.fastq
  5775000 data/samples/B.fastq
  5775000 data/samples/C.fastq
```




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


