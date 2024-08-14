# -*- coding: utf-8 -*-
"""
@author: Jan Bot
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
"""


class TokenGenerator:
    """
    Object to generate the standard tokens with.
    """
    def __init__(self):
        pass

    @staticmethod
    def get_empty_token():
        """Generate empty token"""
        token = {
                'lock': 0,
                'done': 0,
                'hostname': '',
                'scrub_count': 0,
                'type': 'token'
        }
        return token
