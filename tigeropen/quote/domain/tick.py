# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class TradeTick(object):
    def __init__(self):
        self.index = None
        self.timestamp = None
        self.price = None
        self.size = None
        self.direction = None
