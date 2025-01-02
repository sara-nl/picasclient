'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushTokens.py
description:
   Connects to PiCaS server
   Creates three tokens, two for single-core, one for multi-core
   Loads the tokens
'''

import sys
import os
import couchdb
import random

from examples import picasconfig

def getNextIndex():
    db = get_db()
    
    index = 0
    while db.get(f"token_{index}") is not None:
        index+=1

    return index

def loadTokens(db, ncores=1):
    i = getNextIndex()

    token = {
        '_id': 'token_' + str(i),
        'type': 'token',
        'lock': 0,
        'done': 0,
        'hostname': '',
        'scrub_count': 0,
        'input': 'echo $SLURM_CPUS_PER_TASK',
        'exit_code': '',
        'cores': f'{ncores}'
    }
    db.update([token])

def get_db():
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username,pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db

if __name__ == '__main__':
   #Create a connection to the server
   db = get_db()
   #Load the tokens to the database
   loadTokens(db, ncores=1)
   loadTokens(db, ncores=1)
   loadTokens(db, ncores=4)
