"""
@author Joris Borgdorff
"""

import socket
import mimetypes
import base64
import traceback
from uuid import uuid4

from . import jobid
from .util import merge_dicts, seconds


class Document:
    """A CouchDB document."""

    def __init__(self, data=None, base=None):
        if data is None:
            data = {}
        if base is None:
            base = {}
        if isinstance(data, Document):
            data = data.value

        # Data is not from the database
        if '_rev' not in data:
            data = merge_dicts(base, data)

        self.doc = data

    # Python Dict emulation:
    # docs.python.org/2/reference/datamodel.html#emulating-container-types
    def __len__(self):
        return self.doc.__len__()

    def __getitem__(self, idx):
        return self.doc.__getitem__(idx)

    def __setitem__(self, idx, value):
        return self.doc.__setitem__(idx, value)

    def __delitem__(self, idx):
        return self.doc.__delitem__(idx)

    def __contains__(self, idx):
        return self.doc.__contains__(idx)

    def __iter__(self):
        return self.doc.__iter__()
    # End python dict emulation

    @property
    def id(self):
        """id getter"""
        try:
            return self.doc['_id']
        except KeyError as ex:
            raise AttributeError("_id for document is not set") from ex

    @property
    def rev(self):
        """revision getter"""
        try:
            return self.doc['_rev']
        except KeyError as ex:
            raise AttributeError("_rev is not available: document is not "
                                 "retrieved from database") from ex

    @id.setter
    def id(self, new_id):
        """id setter"""
        self.doc['_id'] = new_id

    @property
    def value(self):
        """doc getter"""
        return self.doc

    def update(self, values):
        """Add the output of the RunActor to the task."""
        self.doc.update(values)

    def put_attachment(self, name, data, mimetype=None):
        """
        Put an attachment in the document.

        The attachment data must be provided as str in Python 2 and bytes in
        Python 3.

        The mimetype, if not provided, is guessed from the filename and
        defaults to text/plain.
        """
        if '_attachments' not in self.doc:
            self.doc['_attachments'] = {}

        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(name)
            if mimetype is None:
                mimetype = 'text/plain'

        # Ensure that the entered string is encoded as bytestring for base64
        if isinstance(data, bytes):
            pass
        else:
            data = data.encode()

        b64data = base64.b64encode(data)
        self.doc['_attachments'][name] = {
            'content_type': mimetype, 'data': b64data.decode()}

    def get_attachment(self, name, retrieve_from_database=None):
        """
        Gets an attachment dict from the document.
        Attachment data may not have been copied over from the
        database, in that case it will have an md5 checksum.
        A CouchDB database may be set in retrieve_from_database to retrieve
        the data if it is not present.

        The attachment data will be returned as str in Python 2 and bytes in
        Python 3.

        Raises KeyError if attachment does not exist.
        """
        # Copy all attributes except data, it may be very large
        attachment = {}
        for key in self.doc['_attachments'][name]:
            if key != 'data':
                attachment[key] = self.doc['_attachments'][name][key]

        if 'data' in self.doc['_attachments'][name]:
            attachment['data'] = base64.b64decode(
                self.doc['_attachments'][name]['data'])
        elif retrieve_from_database is not None:
            db = retrieve_from_database.db
            f_attach = db.get_attachment(self.id, name)
            try:
                attachment['data'] = f_attach.read()
            finally:
                f_attach.close()

            b64data = base64.b64encode(attachment['data'])
            self.doc['_attachments'][name]['data'] = b64data

        return attachment

    def remove_attachment(self, name):
        """Remove attachment from document"""
        del self.doc['_attachments'][name]
        return self

    def _update_hostname(self):
        """Set hostname in document"""
        self.doc['hostname'] = socket.gethostname()
        return self


class User(Document):
    """
    CouchDB user
    """
    def __init__(self, username, password, roles=None, data=None):
        if roles is None:
            roles = []
        if data is None:
            data = {}
        super().__init__(
            data=data,
            base={
                '_id': f'org.couchdb.user:{username}',
                'name': username,
                'type': 'user',
                'password': password,
                'roles': roles,
            })


class Task(Document):
    """
    Class to manage task modifications with.
    """
    __BASE = {
        'type': 'task',
        'lock': 0,
        'done': 0,
        'hostname': '',
        'scrub_count': 0,
        'input': {},
        'exit_code': '',
        'output': {},
        'uploads': {},
        'error': [],
    }

    def __init__(self, task=None):
        if task is None:
            task = {}
        super().__init__(task, Task.__BASE)
        if '_id' not in self.doc:
            self.doc['_id'] = 'task_' + uuid4().hex

    def lock(self):
        """Function which modifies the task such that it is locked."""
        self.doc['lock'] = seconds()
        jobid.add_job_id(self.doc)
        return self._update_hostname()

    def done(self):
        """
        Function which modifies the task such that it is closed for ever
        to the view that has supplied it.
        """
        self.doc['done'] = seconds()
        return self

    @property
    def input(self):
        """Get input"""
        return self.doc['input']

    @input.setter
    def input(self, value):
        """Set input"""
        self.doc['input'] = value

    @property
    def output(self):
        """Get the output from the RunActor."""
        return self.doc['output']

    @output.setter
    def output(self, output):
        """Add the output of the RunActor to the task."""
        self.doc['output'] = output

    @property
    def uploads(self):
        """Uploads getter"""
        return self.doc['uploads']

    @uploads.setter
    def uploads(self, uploads):
        """Uploads setter"""
        self.doc['uploads'] = uploads

    def scrub(self):
        """
        Task scrubber: makes sure a task can be handed out again if it was
        locked more than t seconds ago.
        """
        if 'scrub_count' not in self.doc:
            self.doc['scrub_count'] = 0
        self.doc['scrub_count'] += 1
        self.doc['done'] = 0
        self.doc['lock'] = 0
        jobid.remove_job_id(self.doc)
        return self._update_hostname()

    def error(self, msg=None, exception=None):
        """Set error message in the document"""
        error = {'time': seconds()}
        if msg is not None:
            error['message'] = str(msg)

        if exception is not None:
            error['exception'] = traceback.format_exc()

        self.doc['lock'] = 99
        self.doc['done'] = 99
        if 'error' not in self.doc:
            self.doc['error'] = []
        self.doc['error'].append(error)
        return self

    def has_error(self):
        """Bool: check if document has an error"""
        return self.doc['lock'] == 99

    def get_errors(self):
        """Get document error"""
        try:
            return self.doc['error']
        except KeyError():
            return []

    def is_done(self):
        """Bool: is document done"""
        return self.doc['done'] != 0


class Job(Document):
    """
    Job class is more explicit in the timing and archives the work.
    """
    __BASE = {
        'type': 'job',
        'hostname': '',
        'start': 0,
        'done': 0,
        'queue': 0,
        'method': '',
        'archive': 0,
    }

    def __init__(self, job):
        super().__init__(job, Job.__BASE)
        if '_id' not in self.doc:
            raise ValueError('Job ID must be set')

    def queue(self, method, host=None):
        """Set queue time"""
        self.doc['method'] = method
        if host is not None:
            self.doc['hostname'] = host
        self.doc['queue'] = seconds()
        return self

    def start(self):
        """Set start time"""
        self.doc['start'] = seconds()
        self.doc['done'] = 0
        self.doc['archive'] = 0
        return self._update_hostname()

    def finish(self):
        """Set end time"""
        self.doc['done'] = seconds()
        return self

    def archive(self):
        """Set archive time"""
        if self.doc['done'] <= 0:
            self.doc['done'] = seconds()
        self.doc['archive'] = seconds()
        self.id = 'archived-' + self.id + '-' + str(seconds())
        del self.doc['_rev']
        return self

    def is_done(self):
        """Bool: is done"""
        return self.doc['done'] != 0
