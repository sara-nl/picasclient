"""
@author Joris Borgdorff
"""

import base64
import unittest

from picas.documents import Document, Task
from picas.util import seconds


test_id = 'mydoc'
test_other_id = 'myotherdoc'


class TestTask(unittest.TestCase):

    def setUp(self):
        self.task = Task({'_id': test_id})

    def test_create(self):
        doc = Document({'_id': test_id})
        self.assertEqual(doc.id, test_id)
        self.assertEqual(doc.value, {'_id': test_id})
        doc.id = test_other_id
        self.assertEqual(doc.id, test_other_id)
        self.assertEqual(doc.value, {'_id': test_other_id})

    # def test_no_id(self):
    #     doc = Document({'someattr': 1})
    #     self.assertRaises(AttributeError, getattr(doc), 'id')
    #     self.assertRaises(AttributeError, getattr(doc), 'rev')

    def test_empty(self):
        Document({})

    def test_attachment(self):
        doc = Document()
        data = b"This is it"
        textfile = "mytest.txt"
        jsonfile = "mytest.json"
        doc.put_attachment(textfile, data)
        attach = doc.get_attachment(textfile)
        self.assertEqual(attach['content_type'], 'text/plain')
        self.assertEqual(attach['data'], data)
        self.assertEqual(doc['_attachments'][textfile]['data'],
                         base64.b64encode(data).decode())
        doc.remove_attachment(textfile)
        self.assertTrue(textfile not in doc['_attachments'])
        self.assertEqual(attach['data'], data)
        doc.put_attachment(jsonfile, b'{}')
        attach = doc.get_attachment(jsonfile)
        self.assertEqual(attach['content_type'], 'application/json')

    def test_id(self):
        self.assertEqual(self.task.id, test_id)
        self.assertEqual(self.task.value['_id'], test_id)
        self.assertEqual(self.task['_id'], test_id)

    def test_no_id(self):
        t = Task()
        self.assertTrue(len(t.id) > 10)

    def test_done(self):
        self.assertEqual(self.task['done'], 0)
        self.task.done()
        self.assertTrue(self.task['done'] >= seconds() - 1)

    def test_lock(self):
        self.assertEqual(self.task['lock'], 0)
        self.task.lock()
        self.assertTrue(self.task['lock'] >= seconds() - 1)

    def test_scrub(self):
        self.task.lock()
        self.task.done()
        self.task.scrub()
        self.assertEqual(self.task['lock'], 0)
        self.assertEqual(self.task['done'], 0)
        self.assertEqual(self.task['scrub_count'], 1)
        self.task.scrub()
        self.assertEqual(self.task['lock'], 0)
        self.assertEqual(self.task['done'], 0)
        self.assertEqual(self.task['scrub_count'], 2)

    def test_error(self):
        self.task.error("some message")
        self.assertEqual(self.task['lock'], -1)
        self.assertEqual(self.task['done'], -1)
        self.task.scrub()
        self.assertEqual(self.task['lock'], 0)
        self.assertEqual(self.task['done'], 0)
        self.assertEqual(len(self.task['error']), 1)
