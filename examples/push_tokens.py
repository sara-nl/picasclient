#!/usr/bin/env python
"""
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

Push tokens to the PiCaS database for various examples.

The list of supported examples are:
    - quick: push tokens for a quick example that just echos the input value
    - fractals: push tokens for an example that runs the fractals executable
    - autopilot: push tokens for an example that runs pilot jobs on slurm that checks for work loads

Usage:
    # general usage
    python push_tokens.py <example>

    # Push tokens for the quick example
    python push_tokens.py

    # Push tokens for the fractals example
    python push_tokens.py fractals


Description:
   - Connects to PiCaS server
   - Creates tokens for <example>: "quick", "fractals, or "autopilot"
   - Upload/Save the tokens to the database
"""
import subprocess
import picasconfig
from picas.clients import CouchDB
from picas.documents import Task
from create_tokens import create_tokens
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='push_tokens.py',
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'example',
        nargs='?',
        choices=['quick', 'fractals', 'autopilot'],
        default='quick',
        help='Example for which tokens will be created and pushed'
    )

    args = parser.parse_args()
    example = args.example

    # create a connection to the server
    db = CouchDB(
        url=picasconfig.PICAS_HOST_URL,
        db=picasconfig.PICAS_DATABASE,
        username=picasconfig.PICAS_USERNAME,
        password=picasconfig.PICAS_PASSWORD)

    # create tokens
    if example == "quick":
        # create tokens with inputs given in file
        tokensfile = "quickExample.txt"
        with open(tokensfile) as f:
            fields = {"input": f.read().splitlines()}
        tokens = create_tokens(fields, offset=db.doc_count())
    elif example == "fractals":
        tokensfile = subprocess.check_output("./create_tokens.sh", text=True).rstrip('\n')
        with open(tokensfile) as f:
            fields = {"input": f.read().splitlines()}
        tokens = create_tokens(fields, offset=db.doc_count())
    elif example == "autopilot":
        # create tokens with number of cores specified
        fields = {"cores": [ 1, 1, 4]}
        tokens = create_tokens(fields, offset=db.doc_count())
        for token in tokens:
            token.input = "echo $SLURM_CPUS_PER_TASK"
    else:
        exit('Unknown example. Options are "quick", "fractals, or "autopilot".')

    # save tokens in database
    db.save_documents(tokens)
