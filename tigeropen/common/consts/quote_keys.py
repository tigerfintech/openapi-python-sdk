# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class QuoteChangeKey(Enum):
    latest_time = 'timestamp'
    latest_price = 'latestPrice'
    prev_close = 'preClose'
    volume = 'volume'
    open = 'open'
    high = 'high'
    low = 'low'
    close = 'close'
    ask_price = 'askPrice'
    ask_size = 'askSize'
    bid_price = 'bidPrice'
    bid_size = 'bidSize'
    minute = 'mi'


@unique
class QuoteKeyType(Enum):
    ALL = None
    QUOTE = 'askPrice,askSize,bidPrice,bidSize,timestamp'
    TRADE = 'open,high,low,close,preClose,volume,timestamp,latestPrice,hourTradingLatestPrice,' \
            'hourTradingVolume,hourTradingPreClose,hourTradingLatestTime'
    TIMELINE = 'mi'
