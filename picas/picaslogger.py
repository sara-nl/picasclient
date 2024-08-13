# -*- coding: utf-8 -*-
"""
@licence: The MIT License (MIT)
@Copyright (c) 2016, Jan Bot
@author: Lodewijk Nauta
"""

import logging

picaslogger = logging.getLogger("PiCaS")
formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
picaslogger.addHandler(ch)
picaslogger.setLevel(logging.INFO)
