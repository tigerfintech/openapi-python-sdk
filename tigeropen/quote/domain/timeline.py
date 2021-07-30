# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class Timeline:
    def __init__(self):
        self.latest_time = None
        self.price = None
        self.avg_price = None
        self.volume = None

    def __repr__(self):
        return "Timeline(%s)" % self.__dict__
