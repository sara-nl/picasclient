'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python pushEventsTokens.py --folder <dCache_directory> --tokenfile <tokenfile> [--event <write/stage>] [--api <dCache_api>]
description:
   Connects to PiCaS server
   Creates token when file is written to a dCache folder or staged (brought online)
   Loads the tokens
'''

import argparse
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
        'input': filename,
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

def arg_parser():
    """
    Arguments parser for optional values of the example
    returns: argparse object
    """
    parser = argparse.ArgumentParser(description="Subscribe to changes in a given dCache directory and create tokens when a new files are added or staged.")
    parser.add_argument("--folder", required=True, type=str, help="dCache directory to track")
    parser.add_argument("--tokenfile", required=True, type=str, help="Name of tokenfile containing macaroon")
    parser.add_argument("--event", required=True, type=str, help="Type of event to track, write or stage?")
    parser.add_argument("--api", default="https://dcacheview.grid.surfsara.nl:22880/api/v1", type=str, help="dCache api endpoint")

    return parser


if __name__ == '__main__':
    #Create a connection to the server
    db = get_db()

    # parse user arguments
    args = arg_parser().parse_args()

    # Get configurations from commandline arguments:
    # dCache folder to follow:
    folder = args.folder
    # tokenfile with macaroon for accessing dCache
    ada_tokenfile = args.tokenfile
    # dCache API endpoint
    api = args.api 
    # Choose which events you want to to follow: "write" or "stage"
    event = args.event

    if event == "write":
        channel_name = "test_" + event    # channel_name = "test_write"
        command = ["ada", "--tokenfile", ada_tokenfile, "--events", channel_name, folder, "--api", api, "--resume", "--force"]
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
    elif event == "stage":
        channel_name = "test_" + event    #channel_name = "test_staged"
        command = ["ada", "--tokenfile", ada_tokenfile, "--report-staged", channel_name, folder, "--api", api, "--resume", "--force"]
        file_change = 0
        filename = ""
        with Popen(command, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
            for line in p.stdout:
                print(line, end='')
                # The initial file status is listed first, after this line we start following staging events
                if "Listening for file status changes.." in line:
                    file_change = 1
                elif "ONLINE_AND_NEARLINE" in line and file_change == 1: 
                    column = line.split()
                    # Sometimes we get two staging events back (possibly bug in ada/dCache)
                    # So check if token has not already been created
                    if column[2] == filename:
                        continue
                    else:
                        filename = column[2]
                        # create token with filename
                        loadTokens(db, filename)
            for line in p.stderr:
                print(line, end='')
    else:
        exit('Unknown option for event. Options are "write" or "stage".')

    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
