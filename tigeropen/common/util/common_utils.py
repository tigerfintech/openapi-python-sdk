# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


def has_value(m, key):
    if not m:
        return False
    if not (key in m):
        return False
    if not m[key]:
        return False
    return True
