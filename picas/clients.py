# -*- coding: utf-8 -*-
"""
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
@author: Jan Bot
@author: Joris Borgdorff
"""

import random
import sys

import couchdb
from couchdb.design import ViewDefinition
from couchdb.http import ResourceConflict, ResourceNotFound

from .documents import Document, Task
from .picaslogger import picaslogger


class CouchDB:
    """
    Client class to handle communication with the CouchDB back-end.
    """
    def __init__(self,
                 url: str ="http://localhost:5984",
                 db: str = "test",
                 username: str = None,
                 password: str = "",
                 ssl_verification: bool = True,
                 create: bool = False):
        """
        Create a CouchClient object.

        :param url: the location where the CouchDB instance is located,
          including the port at which it's listening.
          Default: http://localhost:5984
        :param db: the database to use. Default: test.
        :param username: the username to use for authentication. Default: None.
        :param password: the password to use for authentication. Default: "".
        :param ssl_verification: whether to verify the SSL certificate of the
          server. Default: True.
        :param create: whether to create the database if it does not exist.
        """
        server = couchdb.Server(url)
        if username is not None:
            server.resource.credentials = (username, password)
        if not ssl_verification:
            server.resource.session.disable_ssl_verification()

        if create:
            self.db = server.create(db)
        else:
            self.db = server[db]

    def copy(self) -> "CouchDB":
        """Copy the DB connection."""
        resource = self.db.resource
        try:
            username, password = resource.credentials
        except TypeError:
            username, password = None, ""

        return CouchDB(
            url=resource.url[:-len(self.db.name) - 1],
            db=self.db.name,
            username=username,
            password=password,
            ssl_verification=resource.session._disable_ssl_verification)

    def __getitem__(self, idx: str) -> Document:
        return self.db[idx]

    def get_from_view(self, view: str, **view_params) -> list[Document]:
        """
        Get Documents from the specified view that has task _id as key.

        :param view: name of the view that has a row id coupled to a document
        :param view_params: name of the view optional extra parameters for the
          view.
        :return: a list of Task objects in the view
        """
        result = []
        for doc in self.view(view, **view_params):
            try:
                result.append(self.get(doc.id))
            except ValueError:
                pass  # doc was already deleted

        return result

    def get(self, id: str) -> Document:
        """
        Get raw data associated to the given ID

        :param id: _id string of the task
        """
        data = self.db.get(id)
        if data is None:
            raise ValueError(id + " is not a document ID in the database")

        return Document(data)

    def get_single_from_view(self, view: str, window_size: int = 1, **view_params) -> Document:
        """
        Get a document from the specified view.

        :param view: the view to get the document from.
        :param view_params: the parameters that should be added to the view
          request. Optional.
        :param window_size: the size of the initial request to CouchDB, only
          one record within that set, which is randomly selected, is returned.
        :return: a CouchDB document.
        """
        view = self.view(view, limit=window_size, **view_params)
        row = random.choice(view.rows)
        return self.get(row.id)

    def view(self, view: str, design_doc: str = "Monitor", **view_params) -> couchdb.client.View:
        """
        Get the data from a view

        :param view: name of the view
        :param view_params: the parameters that should be added to the view
        request. Optional.
        :return: iterator over the view; the rows property contains the rows.
        """
        return self.db.view(design_doc + '/' + view, **view_params)

    def save(self, doc: Document) -> Document:
        """
        Save a Document to the database.

        Updates the document to have the new _rev value.

        :param doc: Document object
        :throws couchdb.http.ResourceConflict: when document exists with
                different revision or was deleted.
        """
        _id, _rev = self.db.save(doc.value)
        doc['_rev'], doc['_id'] = _rev, _id
        return doc

    def save_documents(self, docs: list[Document]) -> list[bool]:
        """
        Save a sequence of Documents to the database.

        - If the document was newly created and the _id is already is in the
          database the document will not be added.
        - If the document is an existing document, it will be updated if the
          _rev key matches.

        :param tasks [task1, task2, ...]; tasks for which the save was
                succesful will get new _rev values
        :return: a sequence of [succeeded1, succeeded2, ...] values.
        """
        updated = self.db.update([doc.value for doc in docs])

        result = [False] * len(docs)
        for i, _ in enumerate(docs):
            is_added, _id, _rev = updated[i]
            if is_added:
                docs[i]['_id'], docs[i]['_rev'] = _id, _rev
                result[i] = True

        return result

    def add_view(self,
                 view: str,
                 map_fun: str,
                 *args,
                 reduce_fun: str = None,
                 design_doc: str = "Monitor",
                 **kwargs) -> None:
        """
        Add a view to the database

        All extra parameters are passed to couchdb.design.ViewDefinition

        :param view: name of the view
        :param map_fun: string of the javascript map function
        :param reduce_fun: string of the javascript reduce function (optional)
        :param design_doc: name of the design document (default: Monitor)
        :param args: extra arguments passed to couchdb.design.ViewDefinition
        :param kwargs: extra keyword arguments passed to couchdb.design.ViewDefinition
        :return: None
        """
        definition = ViewDefinition(
            design_doc, view, map_fun, reduce_fun, *args, **kwargs)
        definition.sync(self.db)

    def delete(self, doc: Document) -> None:
        """
        Delete a Document from the database

        The Document must have a valid and current _id and _rev, so they must
        be retrieved from the database and not be altered there in the mean
        time.
        :param doc: Document object
        :raise: ResourceConflict: if the document was updated in the database
        """
        self.db.delete(doc.value)

    def delete_documents(self, docs: list[Document]) -> list[bool]:
        """
        Delete a sequence of Documents from the database.

        The Documents must have a valid and current _id and _rev, so they must
        be retrieved from the database and not be altered there in the mean
        time.

        :param tasks: list of Document objects to be deleted
        :return: array of booleans indicating whether the respective Document
          was deleted.
        """
        result = [True] * len(docs)
        for i, doc in enumerate(docs):
            try:
                self.delete(doc)
            except ResourceConflict as ex:
                picaslogger.info(
                    f"Could not delete document {doc.id} (rev {doc.rev}) due to resource conflict: {str(ex)}",
                    file=sys.stderr)
                result[i] = False
            except Exception as ex:
                picaslogger.info(f"Could not delete document {str(doc)}: {str(ex)}", file=sys.stderr)
                result[i] = False

        return result

    def delete_from_view(self, view: str, design_doc: str = "Monitor") -> list[bool]:
        """
        Delete all documents in a view

        :param view: name of the view from which to delete all documents
        :return: array of booleans indicating whether the respective tasks
          were deleted
        """
        docs = self.get_from_view(view, design_doc=design_doc)
        return self.delete_documents(docs)

    def set_users(self,
                  admins: list[str] = None,
                  members: list[str] = None,
                  admin_roles: list[str] = None,
                  member_roles: list[str] = None) -> None:
        """
        Set permissions for users.

        :param admins: list of admin usernames
        :param members: list of member usernames
        :param admin_roles: list of admin roles
        :param member_roles: list of member roles
        :return: None
        """
        security = self.db.resource.get_json("_security")[2]

        def try_set(value, doc, key, subkey):
            if value is not None:
                try:
                    doc[key][subkey] = value
                except KeyError:
                    doc[key] = {subkey: value}

        try_set(admins, security, 'admins', 'names')
        try_set(members, security, 'members', 'names')
        try_set(admin_roles, security, 'admins', 'roles')
        try_set(member_roles, security, 'members', 'roles')

        self.db.resource.put("_security", security)

    def is_view_nonempty(self, view: str, **view_params) -> bool:
        """
        Database view scanner

        Useful for starting pilot jobs automatically. When a view is non-empty,
        returns true: a pilot can be started.

        :param view: database view to scan for tokens
        :param view_params: optional parameters for the view
        :return: bool
        """
        # To ensure proper logging when design_doc is not passed into is_view_nonempty,
        # the variable is created as the default used in self.view. Otherwise the
        # f-string below breaks on default input.
        design_doc = view_params.setdefault('design_doc', "Monitor")
        try:
            doc = self.get_single_from_view(view, **view_params)
            task = Task(doc)
            picaslogger.debug(doc)
            picaslogger.debug(task['_id'])
            picaslogger.info(f"View {view} under design document {design_doc} is non-empty.")
            return True
        except IndexError as exc:
            picaslogger.info(f"View {view} under design document {design_doc} is empty: {exc}")
            return False
        except ResourceNotFound:
            picaslogger.info(f"Non-existing view and design document passed: {view} in {design_doc}")
            return False

    def doc_count(self) -> int:
        """
        Count number of documents in database

        :return: int
        """
        return self.db.info()['doc_count']
