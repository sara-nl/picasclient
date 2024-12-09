'''

@helpdesk: SURFsara helpdesk <helpdesk@surfsara.nl>

usage: python resetTokens.py [viewname] [locktime]
  e.g. python resetTokens.py Monitor/locked 72

description:
	Connect to PiCaS server
	Reset all Tokens in [viewname] View that have been locked more than [hours] hours,
    defaults to 0 hours to reset all tokens
'''

import sys

import couchdb
from time import time
import picasconfig

def resetDocs(db, viewname="Monitor/locked", locktime=0):
    v = db.view(viewname)
    max_age = locktime * 3600
    to_update = []
    for x in v:
        document = db[x['key']]
        age = time() - document["lock"]
        print(age)
        if (age > max_age):
            document['lock'] = 0
            document['done'] = 0
            document['scrub_count'] += 1
            document['hostname'] = ''
            document['exit_code'] = ''
            if '_attachments' in document:
                del document["_attachments"]
            to_update.append(document)
    db.update(to_update)
    print("Number of reset tokens: " + str(len(to_update)))


def get_db():
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username, pwd)
    db = server[picasconfig.PICAS_DATABASE]
    return db


if __name__ == '__main__':
    # Create a connection to the server
    db = get_db()

    if len(sys.argv)==1:
        sys.exit("Error: No viewname provided. To reset all locked tokens: `python resetTokens.py Monitor/locked`") 
    elif len(sys.argv)>1:
        # reset the Docs in [viewname]
        viewname = str(sys.argv[1])
    if len(sys.argv)==2:
        print("Warning: No locktime provided. Will reset all tokens in view ", viewname)
        input("Press Enter to continue or Ctrl+C to cancel.")        
        # default: reset all locked tokens 
        locktime=0
    else:
        locktime=float(sys.argv[2])


    resetDocs(db, viewname, locktime)
