#! /usr/bin/env python3
"""
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python createViews.py [picas_db_name] [picas_username] [picas_pwd]
description: create the following Views in [picas_db_name]:
    todo View : lock_timestamp == 0 && done_timestamp == 0
    locked View : lock_timestamp > 0 && done_timestamp == 0
    done View : lock_timestamp > 0 && done _timestamp > 0 && exit_code == 0
    error View : lock_timestamp > 0 && done _timestamp > 0 && exit_code != 0
    overview_total View : sum tokens per View (Map/Reduce)
"""

import argparse
import couchdb
from couchdb.design import ViewDefinition
import picasconfig


def get_view_code(s: str) -> str:
    # double { } are needed for formatting
    general_view_code = '''
function(doc) {{
   if(doc.type == "token") {{
    if({0}) {{
      emit(doc._id, doc._id);
    }}
  }}
}}
'''
    return general_view_code.format(s)


def create_views(db: couchdb.Database,
                 design_doc_name: str = 'Monitor',
                 logic_appendix: str = '') -> None:
    """
    Create the Views in the Picas database.

    :param db: The Picas database connection.
    :param design_doc_name: The name of the design document to create.
    :param logic_appendix: Additional logic to append to the view conditions.
    :raises ValueError: If the design document already exists.
    """
    # todo view
    todo_condition = 'doc.lock == 0 && doc.done == 0'
    todo_condition = todo_condition + logic_appendix
    todo_view = ViewDefinition(design_doc_name, 'todo', get_view_code(todo_condition))
    todo_view.sync(db)

    # locked view
    locked_condition = 'doc.lock > 0 && doc.done == 0'
    locked_condition = locked_condition + logic_appendix
    locked_view = ViewDefinition(design_doc_name, 'locked', get_view_code(locked_condition))
    locked_view.sync(db)

    # done view
    done_condition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0'
    done_condition = done_condition + logic_appendix
    done_view = ViewDefinition(design_doc_name, 'done', get_view_code(done_condition))
    done_view.sync(db)

    # error view
    error_condition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0'
    error_condition = error_condition + logic_appendix
    error_view = ViewDefinition(design_doc_name, 'error', get_view_code(error_condition))
    error_view.sync(db)

    # overview_total view -- lists all views and the number of tokens in each view
    overview_map_code = f'''
function(doc) {{
   if(doc.type == "token") {{
       if ({todo_condition}){{
          emit('todo', 1);
       }}
       if({locked_condition}) {{
          emit('locked', 1);
       }}
       if({done_condition}) {{
          emit('done', 1);
       }}
       if({error_condition}) {{
          emit('error', 1);
       }}
   }}
}}
'''
    overview_reduce_code = '''
function (key, values, rereduce) {
   return sum(values);
}
'''
    overview_total_view = ViewDefinition(
        design_doc_name,
        'overview_total',
        overview_map_code,
        overview_reduce_code)
    overview_total_view.sync(db)


def get_db() -> couchdb.Database:
    """
    Get the Picas database connection from the picasconfig module.
    """
    server = couchdb.Server(picasconfig.PICAS_HOST_URL)
    username = picasconfig.PICAS_USERNAME
    pwd = picasconfig.PICAS_PASSWORD
    server.resource.credentials = (username, pwd)
    db = server[picasconfig.PICAS_DATABASE]

    return db


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Create CouchDB views in Picas database",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        'example',
        nargs='?',
        choices=['autopilot'],
        help='Optional example type to create specific views for'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # create a connection to the server
    db = get_db()

    # create the views in database
    if args.example is None:
        create_views(db)
    elif args.example == "autopilot":
        # create the views for the autopilot example
        create_views(db, design_doc_name='SingleCore', logic_appendix=' && doc.cores == 1')
        create_views(db, design_doc_name='MultiCore', logic_appendix=' && doc.cores == 4')
    else:
        exit('Unknown example. Can only create extra views for example "autopilot".')
