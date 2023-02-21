# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import re

CAMEL_PATTERN = re.compile(r'([a-z]|\d)([A-Z])')


def add_start_end(key, start_marker, end_marker):
    if key.find(start_marker) < 0:
        key = start_marker + key
    if key.find(end_marker) < 0:
        key = key + end_marker
    return key


def camel_to_underline(hunp_str):
    return re.sub(CAMEL_PATTERN, r'\1_\2', hunp_str).lower()


def camel_to_underline_obj(d):
    if isinstance(d, list):
        return [camel_to_underline_obj(i) if isinstance(i, (dict, list)) else i for i in d]
    return {camel_to_underline(k): camel_to_underline_obj(v) if isinstance(v, (dict, list)) else v
            for k, v in d.items()}


def underline_to_camel(underline_str):
    parts = underline_str.split('_')
    return parts[0] + ''.join(x.title() for x in parts[1:])
