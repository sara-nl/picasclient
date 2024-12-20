import random

from picas.documents import Document


class MockDB(object):
    TASKS = [{'_id': 'a', '_rev': '1', 'lock': 0, 'scrub_count': 0},
             {'_id': 'b', '_rev': '1', 'lock': 0, 'scrub_count': 0},
             {'_id': 'c', '_rev': '1', 'lock': 0, 'scrub_count': 0}]
    JOBS = [{'_id': 'myjob'}]

    def __init__(self):
        self.tasks = dict((t['_id'], t.copy())
                          for t in MockDB.TASKS)  # deep copy
        self.jobs = dict((t['_id'], t.copy()) for t in MockDB.JOBS)
        self.saved = {}

    def get_single_from_view(self, view, **view_params):
        idx = random.choice(list(self.tasks.keys()))
        return Document(self.tasks[idx])

    def get(self, idx):
        if idx in self.saved:
            return Document(self.saved[idx])
        elif idx in self.tasks:
            return Document(self.tasks[idx])
        elif idx in self.jobs:
            return Document(self.jobs[idx])
        else:
            raise KeyError

    def save(self, doc):
        doc['_rev'] = 'something'

        if doc.id in self.jobs:
            self.jobs[doc.id] = doc.value
        else:
            if doc.id in self.tasks:
                del self.tasks[doc.id]
            self.saved[doc.id] = doc.value

        return doc

    def copy(self):
        return self


class MockEmptyDB(MockDB):
    TASKS = []
    JOBS = []

    def __init__(self):
        self.tasks = dict((t['_id'], t.copy())
                          for t in MockEmptyDB.TASKS)  # deep copy
        self.jobs = dict((t['_id'], t.copy()) for t in MockEmptyDB.JOBS)
        self.saved = {}
