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

Token commands
========

For the most used commands for preparing and editing tokens, check [Picas token commands](/docs/token-commands.md).


Examples
========

There is a [quick example](/docs/quick-example.md) which lasts for a few minutues. Additionally, a [fractal example](/docs/fractal-example.md) is available for running long jobs.



Check job status
========

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
