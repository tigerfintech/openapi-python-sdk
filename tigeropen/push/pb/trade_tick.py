# -*- coding: utf-8 -*-
# 
# @Date    : 2023/6/1
# @Author  : sukai
class TradeTickItem:
    def __int__(self):
        self.tick_type = None
        self.price = None
        self.volume = None
        self.part_code = None
        self.part_code_name = None
        self.cond = None
        self.time = None
        self.sn = None

    def __repr__(self):
        return f'TradeTickItem<{self.__dict__}>'

class TradeTick:
    def __int__(self):
        self.symbol = None
        self.sec_type = None
        self.quote_level = None
        self.timestamp = None
        self.ticks = None

    def __repr__(self):
        return f'TradeTick<{self.__dict__}>'