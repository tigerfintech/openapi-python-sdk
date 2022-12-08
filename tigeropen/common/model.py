# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/12
# @Author  : sukai


class BaseParams:
    def __init__(self):
        self._version = None  # api版本
        self._lang = None  # language

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.lang:
            params['lang'] = self.lang
        if self.version:
            params['version'] = self.version
        return params


