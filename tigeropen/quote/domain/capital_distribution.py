# -*- coding: utf-8 -*-
# 
# @Date    : 2022/12/9
# @Author  : sukai
class CapitalDistribution:
    def __init__(self):
        self.symbol = None
        self.net_inflow = None
        self.in_all = None
        self.in_big = None
        self.in_mid = None
        self.in_small = None
        self.out_all = None
        self.out_big = None
        self.out_mid = None
        self.out_small = None

    def __repr__(self):
        return "CapitalDistribution(%s)" % self.__dict__
