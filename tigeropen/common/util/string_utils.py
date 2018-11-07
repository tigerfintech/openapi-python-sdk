# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import re

from tigeropen.common.consts import PYTHON_VERSION_3


def add_start_end(key, start_marker, end_marker):
    if key.find(start_marker) < 0:
        key = start_marker + key
    if key.find(end_marker) < 0:
        key = key + end_marker
    return key


def camel_to_underline(hunp_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def get_string(value):
    if PYTHON_VERSION_3:
        return value
    else:
        return value.encode('utf-8')
