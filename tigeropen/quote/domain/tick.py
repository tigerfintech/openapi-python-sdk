# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class TradeTick:
    def __init__(self):
        self.index = None
        self.timestamp = None
        self.price = None
        self.size = None
        self.direction = None

    def __repr__(self):
        return "TradeTick(%s)" % self.__dict__
