'''

@helpdesk: SURFsara helpdesk <helpdesk@surfsara.nl>

usage: python deleteTokens.py [viewname]
  e.g. python deleteTokens.py Monitor/todo

description:
	Connect to PiCaS server
	Delete all the Tokens in the [viewname] View
'''

import sys

import couchdb
import picasconfig


def deleteDocs(db, viewname):
    # v=db.view("Monitor/todo")
    v = db.view(viewname)
    for x in v:
        document = db[x['key']]
        db.delete(document)


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
    # Delete the Docs in [viewname]
    viewname = str(sys.argv[1])
    deleteDocs(db, viewname)
