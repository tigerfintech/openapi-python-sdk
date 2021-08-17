# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class MarketStatus:
    def __init__(self, market, status, open_time, trading_status):
        self.market = market
        self.status = status
        self.open_time = open_time
        self.trading_status = trading_status

    def __repr__(self):
        """
        String representation for this object.
        """
        return "MarketStatus(%s)" % self.__dict__
