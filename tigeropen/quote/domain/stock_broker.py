# -*- coding: utf-8 -*-
# 
# @Date    : 2022/12/9
# @Author  : sukai

class Broker:
    def __init__(self):
        self.id = None
        self.name = None

    def __repr__(self):
        return "Broker(%s)" % self.__dict__


class LevelBroker:
    def __init__(self):
        self.level = None
        self.price = None
        self.broker_count = None
        self.broker = None

    def __repr__(self):
        return "LevelBroker(%s)" % self.__dict__


class StockBroker:
    def __init__(self):
        self.symbol = None
        self.bid_broker = None
        self.ask_broker = None

    def __repr__(self):
        return "StockBroker(%s)" % self.__dict__
