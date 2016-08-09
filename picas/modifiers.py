# -*- coding: utf-8 -*-
"""
The MIT License (MIT)

Copyright (c) 2016, Jan Bot

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Created on Mon Jun  4 11:29:47 2012

@author: Jan Bot
"""

# Python imports
import socket
import time


class TokenModifier(object):

    def __init__(self, timeout=86400):
        self.timeout = timeout

    def lock(self, *args, **kwargs):
        raise NotImplementedError("Lock function not implemented.")

    def unlock(self, *args, **kwargs):
        raise NotImplementedError("Unlock functin not implemented.")

    def close(self, *args, **kwargs):
        raise NotImplementedError("Close function not implemented.")

    def unclose(self, *args, **kwargs):
        raise NotImplementedError("Unclose function not implemented.")

    def add_output(self, *args, **kwargs):
        raise NotImplementedError("Add_output function not implemented.")

    def scrub(self, *args, **kwargs):
        raise NotImplementedError("Scrub function not implemented.")

    def set_error(self, *args, **kwargs):
        raise NotImplementedError("set_error function not implemented.")


class BasicTokenModifier(TokenModifier):

    """Class to manage token modifications with.
    """

    def __init__(self):
        pass

    def lock(self, token):
        """Function which modifies the token such that it is locked.
        @param key: the key generated by the couchdb view.
        @param token: the token content.
        @return: modified token.
        """
        lock_content = {
            'hostname': socket.gethostname(),
            'lock': int(time.time())
        }
        token.update(lock_content)
        return token

    def unlock(self, token):
        """Reset the token to its unlocked state.
        @param key: the key generated by the couchdb view.
        @param token: the token content.
        @return: modified token.
        """
        lock_content = {
            'hostname': socket.gethostname(),
            'lock': 0
        }
        token.update(lock_content)
        return token

    def close(self, token):
        """Function which modifies the token such that it is closed for ever
        to the view that has supplied it.
        @param key: the key generated by the couchdb view.
        @param token: the token content.
        @return: modified token.
        """
        done_content = {
            'done': int(time.time())
        }
        token.update(done_content)
        return token

    def unclose(self, token):
        """Reset the token to be fetched again.
        @param key: the key generated by the CouchDB view.
        @param token: the token content.
        @return: modified token.
        """
        done_content = {
            'done': 0
        }
        token.update(done_content)
        return token

    def add_output(self, token, output):
        """Add the output of the RunActor to the token.
        @param key: the key generated by the CouchDB view.
        @param token: the token content.
        @param output: The output to be included in the token.
        @return: modified token.
        """
        token.update(output)
        return token

    def scrub(self, token):
        """Token scrubber: makes sure a token can be handed out again.
        @param token: the token that needs to be scrubbed.
        @return the scrubbed token. Should be uploaded to the server to finish
         the process.
        """
        if not 'scrub_count' in token:
            token['scrub_count'] = 0
        token['scrub_count'] += 1
        token = self.unlock(token)
        return token

    def set_error(self, token):
        token['lock'] = -1
        token['done'] = -1
        return token


class NestedTokenModifier(TokenModifier):

    def __init__(self, timeout=86400):
        self.timeout = timeout

    def _get_token_from_list(self, ref, record):
        token = record
        for k in ref[1:]:
            token = token[k]
        return token

    def _get_token_from_value(self, ref, record):
        return record[ref]

    def _get_token(self, ref, record):
        if(type(ref) == list):
            return self._get_token_from_list(ref, record)
        else:
            return self._get_token_from_value(ref, record)

    def get_token(self, ref, record):
        return self._get_token(ref, record)

    def _update_record(self, ref, record, token):
        r = record
        if(type(ref)) == list:
            for k in ref[1:len(ref) - 1]:
                r = r[k]
            r[ref[-1]] = token
        else:
            record[ref] = token
        return record

    def lock(self, ref, record):
        token = self._get_token(ref, record)
        token['lock'] = int(time.time())
        token['hostname'] = socket.gethostname()
        return self._update_record(ref, record, token)

    def unlock(self, ref, record):
        token = self._get_token(ref, record)
        token['lock'] = 0
        return self._update_record(ref, record, token)

    def close(self, ref, record):
        token = self._get_token(ref, record)
        token['done'] = int(time.time())
        return self._update_record(ref, record, token)

    def unclose(self, ref, record):
        token = self._get_token(ref, record)
        token['lock'] = 0
        token['done'] = 0
        return self._update_record(ref, record, token)

    def add_output(self, ref, record, output):
        token = self._get_token(ref, record)
        token['output'].update(output)
        return self._update_record(ref, record, token)

    def scrub(self, ref, record):
        token = self._get_token(ref, record)
        token['hostname'] = ""
        token['lock'] = 0
        token['done'] = 0
        token['scrub_count'] += 1
        return self._update_record(ref, record, token)

    def set_error(self, ref, record):
        token = self._get_token(ref, record)
        token['lock'] = -1
        token['done'] = -1
        return self._update_record(ref, record, token)
