import base64

from picas.documents import Document, Task
from picas.util import seconds
from nose.tools import assert_equals, assert_raises, assert_true

''' @author Joris Borgdorff '''

test_id = 'mydoc'
test_other_id = 'myotherdoc'


def test_create():
    doc = Document({'_id': test_id})
    assert_equals(doc.id, test_id)
    assert_equals(doc.value, {'_id': test_id})
    doc.id = test_other_id
    assert_equals(doc.id, test_other_id)
    assert_equals(doc.value, {'_id': test_other_id})


def test_no_id():
    doc = Document({'someattr': 1})
    assert_raises(AttributeError, getattr, doc, 'id')
    assert_raises(AttributeError, getattr, doc, 'rev')


def test_empty():
    Document({})


def test_attachment():
    doc = Document()
    data = b"This is it"
    textfile = "mytest.txt"
    jsonfile = "mytest.json"
    doc.put_attachment(textfile, data)
    attach = doc.get_attachment(textfile)
    assert_equals(attach['content_type'], 'text/plain')
    assert_equals(attach['data'], data)
    assert_equals(doc['_attachments'][textfile]['data'],
                  base64.b64encode(data).decode())
    doc.remove_attachment(textfile)
    assert_true(textfile not in doc['_attachments'])
    assert_equals(attach['data'], data)
    doc.put_attachment(jsonfile, b'{}')
    attach = doc.get_attachment(jsonfile)
    assert_equals(attach['content_type'], 'application/json')

class TestTask:

    def setup(self):
        self.task = Task({'_id': test_id})

    def test_id(self):
        assert_equals(self.task.id, test_id)
        assert_equals(self.task.value['_id'], test_id)
        assert_equals(self.task['_id'], test_id)

    def test_no_id(self):
        t = Task()
        assert_true(len(t.id) > 10)

    def test_done(self):
        assert_equals(self.task['done'], 0)
        self.task.done()
        assert_true(self.task['done'] >= seconds() - 1)

    def test_lock(self):
        assert_equals(self.task['lock'], 0)
        self.task.lock()
        assert_true(self.task['lock'] >= seconds() - 1)

    def test_scrub(self):
        self.task.lock()
        self.task.done()
        self.task.scrub()
        assert_equals(self.task['lock'], 0)
        assert_equals(self.task['done'], 0)
        assert_equals(self.task['scrub_count'], 1)
        self.task.scrub()
        assert_equals(self.task['lock'], 0)
        assert_equals(self.task['done'], 0)
        assert_equals(self.task['scrub_count'], 2)

    def test_error(self):
        self.task.error("some message")
        assert_equals(self.task['lock'], -1)
        assert_equals(self.task['done'], -1)
        self.task.scrub()
        assert_equals(self.task['lock'], 0)
        assert_equals(self.task['done'], 0)
        assert_equals(len(self.task['error']), 1)
