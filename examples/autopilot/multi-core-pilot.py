"""
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python multi-core-pilot.py
description:
    This is part of the example of scanning a CouchDB database and checking if multiple
    views contain work, where the work is either single-core work (single-core-job.sh and 
    single-core-pilot.py) or multi-core work (multi-core-job.sh and multi-core-pilot.py).
    To run the full example, start the scanner through `python core-scanner.py`
"""


from picas.clients import CouchDB
from picas.modifiers import BasicTokenModifier

from examples import picasconfig
from examples.local_example import ExampleActor

def main():
    client = CouchDB(url=picasconfig.PICAS_HOST_URL, db=picasconfig.PICAS_DATABASE, username=picasconfig.PICAS_USERNAME, password=picasconfig.PICAS_PASSWORD)
    print("Connected to the database %s sucessfully. Now starting work..." %(picasconfig.PICAS_DATABASE))
    modifier = BasicTokenModifier()
    actor = ExampleActor(client, modifier, view="todo4c", design_doc="MonitorCores")
    actor.run(max_total_time=10)

if __name__ == '__main__':
    main()
