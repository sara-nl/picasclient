'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python createViews.py [picas_db_name] [picas_username] [picas_pwd]
description: create the following Views in [picas_db_name]:
    todo View : lock_timestamp == 0 && done_timestamp == 0
    locked View : lock_timestamp > 0 && done_timestamp == 0
    done View : lock_timestamp > 0 && done _timestamp > 0 && exit_code == 0
    error View : lock_timestamp > 0 && done _timestamp > 0 && exit_code != 0
    overview_total View : sum tokens per View (Map/Reduce)
'''

import couchdb
from couchdb.design import ViewDefinition
import picasconfig


def getViewCode(s):
    # double { } are needed for formatting
    generalViewCode='''
function(doc) {{
   if(doc.type == "token") {{
    if({0}) {{
      emit(doc._id, doc._id);
    }}
  }}
}}
'''
    return generalViewCode.format(s)

def createViews(db, design_doc_name='Monitor', logic_appendix=''):
    # todo View
    todoCondition = 'doc.lock == 0 && doc.done == 0'
    todoCondition = todoCondition + logic_appendix
    todo_view = ViewDefinition(design_doc_name, 'todo', getViewCode(todoCondition))
    todo_view.sync(db)
    # locked View
    lockedCondition = 'doc.lock > 0 && doc.done == 0'
    lockedCondition = lockedCondition + logic_appendix
    locked_view = ViewDefinition(design_doc_name, 'locked', getViewCode(lockedCondition))
    locked_view.sync(db)
    # done View
    doneCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0'
    doneCondition = doneCondition + logic_appendix
    done_view = ViewDefinition(design_doc_name, 'done', getViewCode(doneCondition))
    done_view.sync(db)
    # error View
    errorCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0'
    errorCondition = errorCondition + logic_appendix
    error_view = ViewDefinition(design_doc_name, 'error', getViewCode(errorCondition))
    error_view.sync(db)
    # overview_total View -- lists all views and the number of tokens in each view
    overviewMapCode=f'''
function(doc) {{
   if(doc.type == "token") {{
       if ({todoCondition}){{
          emit('todo', 1);
       }}
       if({lockedCondition}) {{
          emit('locked', 1);
       }}
       if({doneCondition}) {{
          emit('done', 1);
       }}
       if({errorCondition}) {{
          emit('error', 1);
       }}
   }}
}}
'''
    overviewReduceCode='''
function (key, values, rereduce) {
   return sum(values);
}
'''
    overview_total_view = ViewDefinition(design_doc_name, 'overview_total', overviewMapCode, overviewReduceCode)
    overview_total_view.sync(db)


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
    # Create the Views in database
    createViews(db)
    # Create the Views for the autopilot example
    #createViews(db, design_doc_name='SingleCore', logic_appendix=' && doc.cores == 1')
    #createViews(db, design_doc_name='MultiCore', logic_appendix=' && doc.cores == 4')
