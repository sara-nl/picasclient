# .. todo Mher:: add a proper argument parser
"""
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushTokens.py <example>
description:

   - Connects to PiCaS server
   - Creates tokens for <example>: "quick", "fractals, or "autopilot"
   - Loads the tokens to the database
"""

import sys
import subprocess
import picasconfig
from picas.clients import CouchDB
from picas.documents import Task


def create_tokens(fields):
    """
    Create the tokens as a list of Task documents.
    """
    tokens = []
    i = db.doc_count()
    for arg in fields:
        for line in fields[arg]:
            token = {
                '_id': 'token_' + str(i),
                'type': 'token',
                arg: line,
            }
            tokens.append(Task(token))
            i += 1

    return tokens

if __name__ == '__main__':

    # choose for which example you are creating tokens
    if len(sys.argv) == 2:
        example = sys.argv[1]
    else:
        exit('Please give example as commandline argument. Options are "quick", "fractals, or "autopilot".')

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
        tokens = create_tokens(fields)
    elif example == "fractals":
        tokensfile = subprocess.check_output("./createTokens", text=True).rstrip('\n')
        with open(tokensfile) as f:
            fields = {"input": f.read().splitlines()}
        tokens = create_tokens(fields)
    elif example == "autopilot":
        # create tokens with number of cores specified
        fields = {"cores": [ 1, 1, 4]}
        tokens = create_tokens(fields)
        for token in tokens:
            token.input = "echo $SLURM_CPUS_PER_TASK"
    else:
        exit('Unknown example. Options are "quick", "fractals, or "autopilot".')

    # Save tokens in database
    db.save_documents(tokens)
