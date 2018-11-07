# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class Bar(object):
    def __init__(self):
        self.time = None
        self.open = None
        self.high = None
        self.low = None
        self.close = None
        self.volume = None

    def __repr__(self):
        """
        String representation for this object.
        """
        return "Bar(%s)" % self.__dict__
