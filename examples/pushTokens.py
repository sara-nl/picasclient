'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushTokens.py [path to tokens file]
description:
   Connects to PiCaS server
   Creates one token for each line in [tokens file]
   Loads the tokens
'''

import sys
import os
import couchdb
import random
import picasconfig

def getNextIndex():
    db = get_db()
    
    index = 0
    while db.get(f"token_{index}") is not None:
        index+=1

    return index

def loadTokens(db):
    tokens = []
    tokensfile = sys.argv[1]
    with open(tokensfile) as f:
        input = f.read().splitlines()

    i = getNextIndex()
    for fractal in input:
        token = {
            '_id': 'token_' + str(i),
            'type': 'token',
            'lock': 0,
            'done': 0,
            'hostname': '',
            'scrub_count': 0,
            'input': fractal,
            'exit_code': ''
        }
        tokens.append(token)
        i = i +1
    db.update(tokens)

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
   loadTokens(db)
