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
    """
    An HTTP-level failure.

    ``status`` is an optional keyword argument carrying the HTTP status received. It
    exists so the authentication layer can tell "credential is invalid" (401) from any
    other failure -- only a 401 is worth refreshing the credential and retrying once.
    Omitted it stays None, exactly as before.
    """

    def __init__(self, *args, status=None):
        super().__init__(*args)
        self.status = status
