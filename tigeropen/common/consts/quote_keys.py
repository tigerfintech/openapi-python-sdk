# -*- coding: utf-8 -*-
from enum import Enum, unique


@unique
class QuoteChangeKey(Enum):
    latest_time = 'latestTime'
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
    timestamp = 'timestamp'
    minute = 'mi'
