# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class ApiException(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self, *args, **kwargs):
        sb = "code=" + str(self.code) + \
             " msg=" + self.msg
        return sb


class RequestException(Exception):
    pass


class ResponseException(Exception):
    pass
