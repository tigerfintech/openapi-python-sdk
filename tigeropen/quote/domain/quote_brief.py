# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class HourTrading:
    def __init__(self):
        self.trading_session = None  # 盘前/盘后
        self.latest_price = None  # 最新价
        self.prev_close = None  # 昨日收盘价
        self.latest_time = None  # 最后交易时间
        self.volume = None  # 成交量

        self.open_price = None  # 开盘价
        self.high_price = None  # 最高价
        self.low_price = None  # 最低价
        self.change = None  # 涨跌额

    def __repr__(self):
        """
        String representation for this object.
        """
        return "HourTrading(%s)" % self.__dict__


class QuoteBrief:
    def __init__(self):
        # contract info
        self.symbol = None  # 股票代号
        self.market = None  # 市场代号
        self.name = None  # 股票名称
        self.sec_type = None  # STK 股票, OPT 期权，WAR窝轮，IOPT牛熊证, FUT期货

        self.latest_price = None  # 最新价
        self.prev_close = None  # 昨日收盘价
        self.latest_time = None  # 最后交易时间
        self.volume = None  # 成交量

        self.open_price = None  # 开盘价
        self.high_price = None  # 最高价
        self.low_price = None  # 最低价
        self.change = None  # 涨跌额

        self.bid_price = None  # 卖盘价
        self.bid_size = None  # 卖盘数量
        self.ask_price = None  # 买盘价
        self.ask_size = None  # 买盘数量

        self.halted = None  # 是否停牌 0: 正常,3: 停牌,4: 退市
        self.delay = None  # 延时分钟
        self.auction = None  # 是否竞价时段（仅港股）
        self.expiry = None  # 到期时间（仅港股)

        self.hour_trading = None  # 盘前盘后数据，可能为空（仅美股

    def __repr__(self):
        return "QuoteBrief(%s)" % self.__dict__
