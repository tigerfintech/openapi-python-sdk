# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/12
# @Author  : sukai
from enum import Enum


class BaseParams:
    def __init__(self):
        self._version = None  # api版本

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value


class Field(Enum):
    pass

