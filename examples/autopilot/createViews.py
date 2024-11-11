'''
@helpdesk: SURF helpdesk <helpdesk@surf.nl>

usage: python createViews.py [picas_db_name] [picas_username] [picas_pwd]
description: create the following Views in [picas_db_name]:
    todo 1 core View : lock_timestamp == 0 && done_timestamp == 0 && cores == 1
    todo 4 core View : lock_timestamp == 0 && done_timestamp == 0 && cores == 4
    locked View : lock_timestamp > 0 && done_timestamp == 0
    done View : lock_timestamp > 0 && done _timestamp > 0 && exit_code == 0
    error View : lock_timestamp > 0 && done _timestamp > 0 && exit_code != 0
    overview_total View : sum tokens per View (Map/Reduce)
'''

import couchdb
from couchdb.design import ViewDefinition
import picasconfig


def createViews(db):
    generalViewCode='''
function(doc) {
   if(doc.type == "token") {
    if(%s) {
      emit(doc._id, doc._id);
    }
  }
}
'''
    # todo 1 core View
    todoCondition = 'doc.lock == 0 && doc.done == 0 && doc.cores == 1'
    todo_view = ViewDefinition('MonitorCores', 'todo1c', generalViewCode %(todoCondition))
    todo_view.sync(db)
    # todo 4 cores View
    todoCondition = 'doc.lock == 0 && doc.done == 0 && doc.cores == 4'
    todo_view = ViewDefinition('MonitorCores', 'todo4c', generalViewCode %(todoCondition))
    todo_view.sync(db)
    # locked View
    lockedCondition = 'doc.lock > 0 && doc.done == 0'
    locked_view = ViewDefinition('MonitorCores', 'locked', generalViewCode %(lockedCondition))
    locked_view.sync(db)
    # done View
    doneCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0'
    done_view = ViewDefinition('MonitorCores', 'done', generalViewCode %(doneCondition))
    done_view.sync(db)
    # error View
    errorCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0'
    error_view = ViewDefinition('MonitorCores', 'error', generalViewCode %(errorCondition))
    error_view.sync(db)
    # overview_total View -- lists all views and the number of tokens in each view
    overviewMapCode='''
function(doc) {
   if(doc.type == "token") {
       if (doc.lock == 0 && doc.done == 0 && doc.cores == 1){
          emit('todo1c', 1);
       }
       if (doc.lock == 0 && doc.done == 0 && doc.cores == 4){
          emit('todo4c', 1);
       }
       if(doc.lock > 0 && doc.done == 0) {
          emit('locked', 1);
       }
       if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0) {
          emit('done', 1);
       }
       if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0) {
          emit('error', 1);
       }
   }
}
'''
    overviewReduceCode='''
function (key, values, rereduce) {
   return sum(values);
}
'''
    overview_total_view = ViewDefinition('MonitorCores', 'overview_total', overviewMapCode, overviewReduceCode)
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
