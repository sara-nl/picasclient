picasclient
-----------

![Test](https://github.com/sara-nl/picasclient/actions/workflows/python-app.yml/badge.svg)

Python client using CouchDB as a token pool server.

Installation
============

Run
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
nosetests tests
```

Examples
========

## Setting up the examples

The scripts directory contains examples to use the picasclient. There are examples for running locally (laptop, cluster login), slurm and the Grid (https://www.egi.eu/). 
To run the examples, first you need to have a CouchDB instance running that functions as the token broker that keeps the tokens and then worker machines can approach the broker to get work. To set up this db, see the [SURF documentation](https://doc.grid.surfsara.nl/en/latest/Pages/Practices/picas/picas_overview.html#picas-server-1).

Once this server is running, you can run the PiCaS examples:
 - Local
 - Slurm
 - Grid

To approach the DB, you have to fill in the `script/picasconfig.py` with the information to log in to your CouchDB instance and the database you want use for storing the work tokens.

Next you have to send some tokens with work to the CouchDB instance. You can send two types of work in this example. For very fast running jobs, send the `quickExample.txt` file with:

```
python pushTokens.py quickExample.txt
```

To send more longer running code (it takes up to 30 minutes per token), do:

```
./createTokens
>>> /tmp/tmp.JoLqcdYZRD
```

And pass the output file to the push tokens code:

```
python pushTokens.py /tmp/tmp.abc123
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

## Running on Slurm

## Running on Grid


## Travis build status

[![Build Status](https://travis-ci.org/sara-nl/picasclient.svg?branch=master)](https://travis-ci.org/sara-nl/picasclient)

## QuantifiedCode Automated code review  

[![Code Issues](https://www.quantifiedcode.com/api/v1/project/b54df6dfb35b4325b6104fb854a1f141/badge.svg)](https://www.quantifiedcode.com/app/project/b54df6dfb35b4325b6104fb854a1f141)
