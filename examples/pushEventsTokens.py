'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushEventsTokens.py <channel> <folder> <write/stage>
description:
   Connects to PiCaS server
   Creates token when file is written to a dCache folder or staged (brought online)
   Loads the tokens
'''

import couchdb
import picasconfig
from subprocess import Popen, PIPE, CalledProcessError

def getNextIndex():
    db = get_db()
    
    index = 0
    while db.get(f"token_{index}") is not None:
        index+=1

    return index

def loadTokens(db, filename):
    i = getNextIndex()

    token = {
        '_id': 'token_' + str(i),
        'type': 'token',
        'lock': 0,
        'done': 0,
        'hostname': '',
        'scrub_count': 0,
        'input': f'echo {filename}',
        'exit_code': '',
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

    #Create a channel to listen to dCache events for a given directory
    folder = "/pnfs/grid.sara.nl/data/users/hailih/tape/testdir/"
    ada_tokenfile = "tokenfile_prod.conf"
    api = "https://dcacheview.grid.surfsara.nl:22880/api/v1"
    channel = "test3"

    command=["ada", "--tokenfile", ada_tokenfile, "--events", channel, folder, "--api", api, "--resume", "--force"]
    #print(command)
    with Popen(command, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')
            if "inotify" in line:
                column = line.split()
                if column[2] == "IN_CLOSE_WRITE":
                    filename = column[1]
                    # create token with filename
                    loadTokens(db, filename)
        for line in p.stderr:
            print(line, end='')

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
