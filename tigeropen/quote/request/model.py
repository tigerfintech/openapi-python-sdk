# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.model import BaseParams


class MarketParams(BaseParams):
    def __init__(self):
        super(MarketParams, self).__init__()
        self._market = None  # 市场
        self._sec_type = None  # 交易品种
        self._lang = None  # 语言

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def sec_type(self):
        return self._sec_type

    @sec_type.setter
    def sec_type(self, value):
        self._sec_type = value

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

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.lang:
            params['lang'] = self.lang

        return params


class SingleQuoteParams(MarketParams):
    def __init__(self):
        super(SingleQuoteParams, self).__init__()
        self._symbol = None
        self._put_call = None  # for option
        self._expiry = None  # for option and future
        self._strike = None  # for option and future
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
    def put_call(self):
        return self._put_call

    @put_call.setter
    def put_call(self, value):
        self._put_call = value

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        self._expiry = value

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value):
        self._strike = value

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

        if self.put_call:
            params['right'] = self.put_call

        if self.expiry:
            params['expiry'] = self.expiry

        if self.strike:
            params['strike'] = self.strike

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
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None
        self._begin_index = None
        self._end_index = None
        self._date = None
        self._page_token = None

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

    @property
    def period(self):
        return self._period

    @period.setter
    def period(self, value):
        self._period = value

    @right.setter
    def right(self, value):
        self._right = value

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
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

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
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def page_token(self):
        return self._page_token

    @page_token.setter
    def page_token(self, value):
        self._page_token = value

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

        if self.period:
            params['period'] = self.period

        if self.begin_time:
            params['begin_time'] = self.begin_time

        if self.end_time:
            params['end_time'] = self.end_time

        if self.limit:
            params['limit'] = self.limit

        if self.begin_index:
            params['begin_index'] = self.begin_index

        if self.end_index:
            params['end_index'] = self.end_index

        if self.date:
            params['date'] = self.date

        if self.page_token:
            params['page_token'] = self.page_token

        return params


class SingleContractParams(BaseParams):
    def __init__(self):
        super(SingleContractParams, self).__init__()
        self._symbol = None
        self._put_call = None  # for option
        self._expiry = None  # for option and future
        self._strike = None  # for option and future

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def put_call(self):
        return self._put_call

    @put_call.setter
    def put_call(self, value):
        self._put_call = value

    @property
    def expiry(self):
        return self._expiry

    @expiry.setter
    def expiry(self, value):
        self._expiry = value

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value):
        self._strike = value

    def to_openapi_dict(self):
        params = dict()

        if self.symbol:
            params['symbol'] = self.symbol

        if self.put_call:
            params['right'] = self.put_call

        if self.expiry:
            params['expiry'] = self.expiry

        if self.strike:
            params['strike'] = self.strike

        return params


class SingleOptionQuoteParams(SingleContractParams):
    def __init__(self):
        super(SingleOptionQuoteParams, self).__init__()
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None

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
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    def to_openapi_dict(self):
        params = super(SingleOptionQuoteParams, self).to_openapi_dict()

        if self.period:
            params['period'] = self.period

        if self.begin_time:
            params['begin_time'] = self.begin_time

        if self.end_time:
            params['end_time'] = self.end_time

        if self.limit:
            params['limit'] = self.limit

        return params


class MultipleContractParams(BaseParams):
    def __init__(self):
        super(MultipleContractParams, self).__init__()
        self._contracts = None  # list of SingleQuoteParams

    @property
    def contracts(self):
        return self._contracts

    @contracts.setter
    def contracts(self, value):
        self._contracts = value

    def to_openapi_dict(self):
        params = list()

        if self.contracts:
            for contract in self.contracts:
                params.append(contract.to_openapi_dict())

        return params


class FutureExchangeParams(BaseParams):
    def __init__(self):
        super(FutureExchangeParams, self).__init__()
        self._exchange_code = None  # 交易所
        self._lang = None  # 语言

    @property
    def exchange_code(self):
        return self._exchange_code

    @exchange_code.setter
    def exchange_code(self, value):
        self._exchange_code = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.exchange_code:
            params['exchange_code'] = self.exchange_code

        if self.lang:
            params['lang'] = self.lang

        return params


class FutureContractParams(BaseParams):
    def __init__(self):
        self._type = None  # 期货品种
        self._contract_code = None  # 期货代码
        self._lang = None  # 语言

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def contract_code(self):
        return self._contract_code

    @contract_code.setter
    def contract_code(self, value):
        self._contract_code = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.type:
            params['type'] = self.type

        if self.contract_code:
            params['contract_code'] = self.contract_code

        if self.lang:
            params['lang'] = self.lang

        return params


class FutureTradingTimeParams(BaseParams):
    def __init__(self):
        super(FutureTradingTimeParams, self).__init__()
        self._contract_code = None
        self._trading_date = None

    @property
    def contract_code(self):
        return self._contract_code

    @contract_code.setter
    def contract_code(self, value):
        self._contract_code = value

    @property
    def trading_date(self):
        return self._trading_date

    @trading_date.setter
    def trading_date(self, value):
        self._trading_date = value

    def to_openapi_dict(self):
        params = dict()
        if self.contract_code:
            params['contract_code'] = self.contract_code

        if self.trading_date:
            params['trading_date'] = self.trading_date

        return params


class FutureQuoteParams(MarketParams):
    def __init__(self):
        super(FutureQuoteParams, self).__init__()
        self._contract_codes = None
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None
        self._begin_index = None
        self._end_index = None
        self._page_token = None

    @property
    def contract_codes(self):
        return self._contract_codes

    @contract_codes.setter
    def contract_codes(self, value):
        self._contract_codes = value

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

    @property
    def page_token(self):
        return self._page_token

    @page_token.setter
    def page_token(self, value):
        self._page_token = value

    def to_openapi_dict(self):
        params = super(FutureQuoteParams, self).to_openapi_dict()

        if self.contract_codes:
            params['contract_codes'] = self.contract_codes

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

        if self.page_token:
            params['page_token'] = self.page_token

        return params


class DepthQuoteParams(BaseParams):
    def __init__(self):
        super(DepthQuoteParams, self).__init__()
        self._symbols = None
        self._market = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    def to_openapi_dict(self):
        params = dict()
        if self.symbols:
            params['symbols'] = self.symbols
        if self.market:
            params['market'] = self.market
        return params


class OptionChainParams(BaseParams):
    def __init__(self):
        super(OptionChainParams, self).__init__()
        self._contracts = None
        self._option_filter = None

    @property
    def contracts(self):
        return self._contracts

    @contracts.setter
    def contracts(self, value):
        self._contracts = value

    @property
    def option_filter(self):
        return self._option_filter

    @option_filter.setter
    def option_filter(self, value):
        self._option_filter = value

    def to_openapi_dict(self):
        params = {'option_basic': list(), 'option_filter': dict()}

        if self.contracts:
            for contract in self.contracts:
                params['option_basic'].append(contract.to_openapi_dict())
        if self.option_filter:
            params['option_filter'] = self.option_filter.to_dict()
        return params
