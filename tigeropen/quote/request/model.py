# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class MarketParams(object):
    def __init__(self):
        self._market = None  # 市场
        self._lang = None  # 语言

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.market:
            params['market'] = self.market

        if self.lang:
            params['lang'] = self.lang

        return params


class SingleQuoteParams(MarketParams):
    def __init__(self):
        super(SingleQuoteParams, self).__init__()
        self._symbol = None
        self._include_hour_trading = None
        self._include_ask_bid = None
        self._right = None
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None
        self._begin_index = None
        self._end_index = None

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def include_hour_trading(self):
        return self._include_hour_trading

    @include_hour_trading.setter
    def include_hour_trading(self, value):
        self._include_hour_trading = value

    @property
    def include_ask_bid(self):
        return self._include_ask_bid

    @include_ask_bid.setter
    def include_ask_bid(self, value):
        self._include_ask_bid = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @property
    def begin_time(self):
        return self._begin_time

    @begin_time.setter
    def begin_time(self, value):
        self._begin_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        self._end_time = value

    @property
    def begin_index(self):
        return self._begin_index

    @begin_index.setter
    def begin_index(self, value):
        self._begin_index = value

    @property
    def end_index(self):
        return self._end_index

    @end_index.setter
    def end_index(self, value):
        self._end_index = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    def to_openapi_dict(self):
        params = super(SingleQuoteParams, self).to_openapi_dict()

        if self.symbol:
            params['symbol'] = self.symbol

        if self.include_hour_trading is not None:
            params['include_hour_trading'] = self.include_hour_trading

        if self.include_ask_bid is not None:
            params['include_ask_bid'] = self.include_ask_bid

        if self.right:
            params['right'] = self.right

        if self.period:
            params['period'] = self.period

        if self.begin_time:
            params['begin_time'] = self.begin_time

        if self.end_time:
            params['end_time'] = self.end_time

        if self.begin_index is not None:
            params['begin_index'] = self.begin_index

        if self.end_index is not None:
            params['end_index'] = self.end_index

        if self.limit:
            params['limit'] = self.limit

        return params


class MultipleQuoteParams(MarketParams):
    def __init__(self):
        super(MultipleQuoteParams, self).__init__()
        self._symbols = None
        self._include_hour_trading = None
        self._include_ask_bid = None
        self._right = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def include_hour_trading(self):
        return self._include_hour_trading

    @include_hour_trading.setter
    def include_hour_trading(self, value):
        self._include_hour_trading = value

    @property
    def include_ask_bid(self):
        return self._include_ask_bid

    @include_ask_bid.setter
    def include_ask_bid(self, value):
        self._include_ask_bid = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    def to_openapi_dict(self):
        params = super(MultipleQuoteParams, self).to_openapi_dict()

        if self.symbols:
            params['symbols'] = self.symbols

        if self.include_hour_trading is not None:
            params['include_hour_trading'] = self.include_hour_trading

        if self.include_ask_bid is not None:
            params['include_ask_bid'] = self.include_ask_bid

        if self.right:
            params['right'] = self.right

        return params
