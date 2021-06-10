# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class QuoteChangeKey(Enum):
    timestamp = 'timestamp'
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
    bid_depth = 'bidDepth'
    ask_depth = 'askDepth'


@unique
class QuoteKeyType(Enum):
    ALL = 'askPrice,askSize,bidPrice,bidSize,open,high,low,close,preClose,volume,latestPrice,mi'  # 所有行情数据
    QUOTE = 'askPrice,askSize,bidPrice,bidSize'  # 盘口数据
    TRADE = 'open,high,low,close,preClose,volume,latestPrice'  # 成交数据
    TIMELINE = 'mi'  # 分时数据
