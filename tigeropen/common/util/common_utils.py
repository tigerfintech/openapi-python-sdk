# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from enum import Enum

import pytz

eastern = pytz.timezone('US/Eastern')
china = pytz.timezone('Asia/Shanghai')
hongkong = pytz.timezone('Asia/Hong_Kong')


def has_value(m, key):
    if not m:
        return False
    if not (key in m):
        return False
    if not m[key]:
        return False
    return True


def get_enum_value(e, enum_type=None):
    if enum_type is None:
        return e.value if isinstance(e, Enum) else e
    return e.value if isinstance(e, enum_type) else e
