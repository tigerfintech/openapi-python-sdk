# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.model import BaseParams
from tigeropen.common.util.string_utils import underline_to_camel


class MarketParams(BaseParams):
    def __init__(self):
        super(MarketParams, self).__init__()
        self._market = None  # 市场
        self._sec_type = None  # 交易品种

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

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.market:
            params['market'] = self.market

        if self.sec_type:
            params['sec_type'] = self.sec_type

        return params


class SymbolsParams(MarketParams):
    def __init__(self):
        super(SymbolsParams, self).__init__()
        self._include_otc = None

    @property
    def include_otc(self):
        return self._include_otc

    @include_otc.setter
    def include_otc(self, value):
        self._include_otc = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.include_otc:
            params['include_otc'] = self.include_otc
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
        self._date = None
        self._page_token = None
        self._trade_session = None

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

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

    @property
    def trade_session(self):
        return self._trade_session

    @trade_session.setter
    def trade_session(self, value):
        self._trade_session = value

    def to_openapi_dict(self):
        params = super(MultipleQuoteParams, self).to_openapi_dict()

        if self.symbols:
            params['symbols'] = self.symbols

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

        if self.limit is not None:
            params['limit'] = self.limit

        if self.begin_index is not None:
            params['begin_index'] = self.begin_index

        if self.end_index is not None:
            params['end_index'] = self.end_index

        if self.date:
            params['date'] = self.date

        if self.page_token:
            params['page_token'] = self.page_token

        if self.trade_session:
            params['trade_session'] = self.trade_session

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
        params = super().to_openapi_dict()

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
        self._sort_dir = None

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

    @property
    def sort_dir(self):
        return self._sort_dir

    @sort_dir.setter
    def sort_dir(self, value):
        self._sort_dir = value

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
        if self.sort_dir:
            params['sort_dir'] = self.sort_dir
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


class OptionContractsParams(BaseParams):
    def __init__(self):
        super(OptionContractsParams, self).__init__()
        self._option_basics = None  # list of SingleQuoteParams
        self._option_query = None
        self._symbols = None
        self._market = None

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def option_basics(self):
        return self._option_basics

    @option_basics.setter
    def option_basics(self, value):
        self._option_basics = value

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

    @property
    def option_query(self):
        return self._option_query

    @option_query.setter
    def option_query(self, value):
        self._option_query = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.market:
            params['market'] = self.market
        if self.symbols:
            params['symbols'] = self.symbols
        if self.option_basics:
            params['option_basic'] = []
            for contract in self.option_basics:
                params['option_basic'].append(contract.to_openapi_dict())
        if self.option_query:
            params['option_query'] = []
            for contract in self.option_query:
                params['option_query'].append(contract.to_openapi_dict())
        return params


class FutureExchangeParams(BaseParams):
    def __init__(self):
        super(FutureExchangeParams, self).__init__()
        self._exchange_code = None  # 交易所

    @property
    def exchange_code(self):
        return self._exchange_code

    @exchange_code.setter
    def exchange_code(self, value):
        self._exchange_code = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.exchange_code:
            params['exchange_code'] = self.exchange_code

        return params


class FutureContractParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._type = None  # 期货品种
        self._contract_code = None  # 期货代码

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

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.type:
            params['type'] = self.type

        if self.contract_code:
            params['contract_code'] = self.contract_code

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
        params = super().to_openapi_dict()
        if self.contract_code:
            params['contract_code'] = self.contract_code

        if self.trading_date:
            params['trading_date'] = self.trading_date

        return params


class FutureQuoteParams(MarketParams):
    def __init__(self):
        super(FutureQuoteParams, self).__init__()
        self._contract_code = None
        self._contract_codes = None
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None
        self._begin_index = None
        self._end_index = None
        self._page_token = None

    @property
    def contract_code(self):
        return self._contract_code

    @contract_code.setter
    def contract_code(self, value):
        self._contract_code = value

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

        if self.contract_code:
            params['contract_code'] = self.contract_code

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
        self._trade_session = None

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

    @property
    def trade_session(self):
        return self._trade_session

    @trade_session.setter
    def trade_session(self, value):
        self._trade_session = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.symbols:
            params['symbols'] = self.symbols
        if self.market:
            params['market'] = self.market
        if self.trade_session:
            params['trade_session'] = self.trade_session
        return params


class OptionChainParams(BaseParams):
    def __init__(self):
        super(OptionChainParams, self).__init__()
        self._contracts = None
        self._option_filter = None
        self._return_greek_value = None
        self._market = None

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

    @property
    def return_greek_value(self):
        return self._return_greek_value

    @return_greek_value.setter
    def return_greek_value(self, value):
        self._return_greek_value = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        params.update({'option_basic': list()})

        if self.contracts:
            for contract in self.contracts:
                params['option_basic'].append(contract.to_openapi_dict())
        if self.option_filter:
            params['option_filter'] = self.option_filter.to_dict()
        if self.return_greek_value is not None:
            params['return_greek_value'] = self.return_greek_value
        if self.market:
            params['market'] = self.market
        return params


class TradingCalendarParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._market = None
        self._begin_date = None
        self._end_date = None

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, value):
        self._begin_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.market:
            params['market'] = self.market

        if self.begin_date:
            params['begin_date'] = self.begin_date

        if self.end_date:
            params['end_date'] = self.end_date

        return params


class MarketScannerParams(BaseParams):
    def __init__(self):
        super(MarketScannerParams, self).__init__()
        self._market = None
        self._base_filter_list = None
        self._accumulate_filter_list = None
        self._financial_filter_list = None
        self._multi_tags_filter_list = None
        self._sort_field_data = None
        self._page = None
        self._page_size = None
        self._multi_tags_fields = None
        self._cursor_id = None

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def base_filter_list(self):
        return self._base_filter_list

    @base_filter_list.setter
    def base_filter_list(self, value):
        self._base_filter_list = value

    @property
    def accumulate_filter_list(self):
        return self._accumulate_filter_list

    @accumulate_filter_list.setter
    def accumulate_filter_list(self, value):
        self._accumulate_filter_list = value

    @property
    def financial_filter_list(self):
        return self._financial_filter_list

    @financial_filter_list.setter
    def financial_filter_list(self, value):
        self._financial_filter_list = value

    @property
    def multi_tags_filter_list(self):
        return self._multi_tags_filter_list

    @multi_tags_filter_list.setter
    def multi_tags_filter_list(self, value):
        self._multi_tags_filter_list = value

    @property
    def sort_field_data(self):
        return self._sort_field_data

    @sort_field_data.setter
    def sort_field_data(self, value):
        self._sort_field_data = value

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value

    @property
    def multi_tags_fields(self):
        return self._multi_tags_fields

    @multi_tags_fields.setter
    def multi_tags_fields(self, value):
        self._multi_tags_fields = value

    @property
    def cursor_id(self):
        return self._cursor_id

    @cursor_id.setter
    def cursor_id(self, value):
        self._cursor_id = value

    def to_openapi_dict(self):
        """
        example
        {"accumulate_filter_list":
            [{"field_name":"AccumulateField_ChangeRate","filter_max":1,"filter_min":0.01,"is_no_filter":false,"period":"Last_Year"}],
        "base_filter_list":
            [{"field_name":"StockField_FloatShare","filter_max":10000000000000.0,"filter_min":10000000.0,"is_no_filter":true},
            {"field_name":"StockField_MarketValue","filter_max":100000000000000.0,"filter_min":100000000.0,"is_no_filter":false}],
        "financial_filter_list":
            [{"field_name":"FinancialField_LYR_PE","filter_max":100,"filter_min":1,"financial_period":"LTM","is_no_filter":false}],
        "multi_tags_filter_list":
            [{"field_name":"MultiTagField_isOTC","is_no_filter":false,"tag_list":[1]}],
        "sort_field_data":{"field_name":13,"field_type":"StockField_Type","sort_dir":"SortDir_Ascend"},
        "page_size":50,
        "market":"US"}
        :return:
        """
        params = super().to_openapi_dict()

        if self.market:
            params['market'] = self.market
        if self.base_filter_list:
            params['base_filter_list'] = self.base_filter_list
        if self.accumulate_filter_list:
            params['accumulate_filter_list'] = self.accumulate_filter_list
        if self.financial_filter_list:
            params['financial_filter_list'] = self.financial_filter_list
        if self.multi_tags_filter_list:
            params['multi_tags_filter_list'] = self.multi_tags_filter_list
        if self.sort_field_data:
            params['sort_field_data'] = self.sort_field_data.to_dict()
        if self.page is not None:
            params['page'] = self.page
        if self.page_size is not None:
            params['page_size'] = self.page_size
        if self.cursor_id is not None:
            params['cursor_id'] = self.cursor_id
        if self.multi_tags_fields:
            params['multi_tag_field_list'] = [f.field_request_name for f in self.multi_tags_fields]
        return params


class StockBrokerParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._symbol = None
        self._limit = None

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.symbol:
            params['symbol'] = self.symbol
        if self.limit:
            params['limit'] = self.limit
        return params

class BrokerHoldParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._market = None
        self._page = None
        self._limit = None
        self._order_by = None
        self._direction = None

    @property
    def market(self):
        return self._market
    @market.setter
    def market(self, value):
        self._market = value
    @property
    def page(self):
        return self._page
    @page.setter
    def page(self, value):
        self._page = value
    @property
    def limit(self):
        return self._limit  
    @limit.setter   
    def limit(self, value): 
        self._limit = value
    @property
    def order_by(self):
        return self._order_by
    @order_by.setter
    def order_by(self, value):
        self._order_by = value
    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self, value):
        self._direction = value
    def to_openapi_dict(self):
        params = super().to_openapi_dict()  
        if self.market:
            params['market'] = self.market
        if self.page is not None and self.page >= 0:
            params['page'] = self.page
        if self.limit:
            params['limit'] = self.limit
        if self.order_by:
            params['order_by'] = self.order_by
        if self.direction:
            params['direction'] = self.direction
        return params



class CapitalParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._symbol = None
        self._market = None
        self._period = None
        self._begin_time = None
        self._end_time = None
        self._limit = None

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

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
        params = super().to_openapi_dict()
        if self.symbol:
            params['symbol'] = self.symbol
        if self.market:
            params['market'] = self.market
        if self.period:
            params['period'] = self.period
        if self.begin_time:
            params['begin_time'] = self.begin_time
        if self.end_time:
            params['end_time'] = self.end_time
        if self.limit:
            params['limit'] = self.limit
        return params


class WarrantFilterParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._symbol = None
        self._page = None
        self._page_size = None
        self._sort_field_name = None
        # sort directions
        self._sort_dir = None
        # 1:Call, 2: Put, 3: Bull,4: Bear, 0: All
        self._warrant_type: set[int] = set()
        self._issuer_name = None
        # expiry date: yyyy-MM
        self._expire_ym = None
        # 0 All, 1 Normal, 2 Terminate Trades, 3 Waiting to be listed
        self._state: int = None
        # -1:out the money, 1: in the money
        self._in_out_price: set[int] = set()
        self._lot_size: set[int] = set()
        self._entitlement_ratio: set[float] = set()

        self._strike: tuple[float, float] = tuple()
        self._effective_leverage: tuple[float, float] = tuple()
        self._leverage_ratio: tuple[float, float] = tuple()
        self._call_price: tuple[float, float] = tuple()
        self._volume: tuple[int, int] = tuple()
        self._premium: tuple[float, float] = tuple()
        self._outstanding_ratio: tuple[float, float] = tuple()
        self._implied_volatility: tuple[int, int] = tuple()

    def set_state(self, value):
        self._state = value

    def set_issuer_name(self, value):
        self._issuer_name = value

    def set_expire_ym(self, value):
        self._expire_ym = value

    def add_warrant_type(self, value):
        self._warrant_type.add(value)

    def add_in_out_price(self, value):
        self._in_out_price.add(value)

    def add_lot_size(self, value):
        self._lot_size.add(value)

    def add_entitlement_ratio(self, value):
        self._entitlement_ratio.add(value)

    def set_strike_range(self, min_value, max_value):
        self._strike = (min_value, max_value)

    def set_effective_leverage_range(self, min_value, max_value):
        self._effective_leverage = (min_value, max_value)

    def set_leverage_ratio_range(self, min_value, max_value):
        self._leverage_ratio = (min_value, max_value)

    def set_call_price_range(self, min_value, max_value):
        self._call_price = (min_value, max_value)

    def set_volume_range(self, min_value, max_value):
        self._volume = (min_value, max_value)

    def set_premium_range(self, min_value, max_value):
        self._premium = (min_value, max_value)

    def set_outstanding_ratio_range(self, min_value, max_value):
        self._outstanding_ratio = (min_value, max_value)

    def set_implied_volatility_range(self, min_value, max_value):
        self._implied_volatility = (min_value, max_value)

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = value

    @property
    def page_size(self):
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        self._page_size = value

    @property
    def sort_field_name(self):
        return self._sort_field_name

    @sort_field_name.setter
    def sort_field_name(self, value):
        self._sort_field_name = value

    @property
    def sort_dir(self):
        return self._sort_dir

    @sort_dir.setter
    def sort_dir(self, value):
        self._sort_dir = value

    @property
    def warrant_type(self):
        return self._warrant_type

    @warrant_type.setter
    def warrant_type(self, value):
        self._warrant_type = value

    @property
    def issuer_name(self):
        return self._issuer_name

    @issuer_name.setter
    def issuer_name(self, value):
        self._issuer_name = value

    @property
    def expire_ym(self):
        return self._expire_ym

    @expire_ym.setter
    def expire_ym(self, value):
        self._expire_ym = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def in_out_price(self):
        return self._in_out_price

    @in_out_price.setter
    def in_out_price(self, value):
        self._in_out_price = value

    @property
    def lot_size(self):
        return self._lot_size

    @lot_size.setter
    def lot_size(self, value):
        self._lot_size = value

    @property
    def entitlement_ratio(self):
        return self._entitlement_ratio

    @entitlement_ratio.setter
    def entitlement_ratio(self, value):
        self._entitlement_ratio = value

    @property
    def strike(self):
        return self._strike

    @strike.setter
    def strike(self, value):
        self._strike = value

    @property
    def effective_leverage(self):
        return self._effective_leverage

    @effective_leverage.setter
    def effective_leverage(self, value):
        self._effective_leverage = value

    @property
    def leverage_ratio(self):
        return self._leverage_ratio

    @leverage_ratio.setter
    def leverage_ratio(self, value):
        self._leverage_ratio = value

    @property
    def call_price(self):
        return self._call_price

    @call_price.setter
    def call_price(self, value):
        self._call_price = value

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value

    @property
    def premium(self):
        return self._premium

    @premium.setter
    def premium(self, value):
        self._premium = value

    @property
    def outstanding_ratio(self):
        return self._outstanding_ratio

    @outstanding_ratio.setter
    def outstanding_ratio(self, value):
        self._outstanding_ratio = value

    @property
    def implied_volatility(self):
        return self._implied_volatility

    @implied_volatility.setter
    def implied_volatility(self, value):
        self._implied_volatility = value

    def convert_range_param(self, value: tuple):
        if (isinstance(value, tuple) or isinstance(value, list)) and len(value) == 2:
            return {'min': value[0], 'max': value[1]}
        return value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.symbol:
            params['symbol'] = self.symbol
        if self.page:
            params['page'] = self.page
        if self.page_size:
            params['page_size'] = self.page_size
        if self.sort_field_name:
            params['sort_field_name'] = underline_to_camel(self.sort_field_name)
        if self.sort_dir:
            params['sort_dir'] = self.sort_dir
        if self.issuer_name:
            params['issuer_name'] = self.issuer_name
        if self.expire_ym:
            params['expire_ym'] = self.expire_ym
        if self.in_out_price:
            params['in_out_price'] = list(self.in_out_price)
        if self.lot_size:
            params['lot_size'] = list(self.lot_size)
        if self.entitlement_ratio:
            params['entitlement_ratio'] = list(self.entitlement_ratio)
        if self.warrant_type:
            params['warrant_type'] = list(self.warrant_type)
        if self.state:
            params['state'] = self.state
        # tuple params
        if self.strike:
            params['strike'] = self.convert_range_param(self.strike)
        if self.effective_leverage:
            params['effective_leverage'] = self.convert_range_param(self.effective_leverage)
        if self.leverage_ratio:
            params['leverage_ratio'] = self.convert_range_param(self.leverage_ratio)
        if self.call_price:
            params['call_price'] = self.convert_range_param(self.call_price)
        if self.volume:
            params['volume'] = self.convert_range_param(self.volume)
        if self.premium:
            params['premium'] = self.convert_range_param(self.premium)
        if self.outstanding_ratio:
            params['outstanding_ratio'] = self.convert_range_param(self.outstanding_ratio)
        if self.implied_volatility:
            params['implied_volatility'] = self.convert_range_param(self.implied_volatility)
        return params


class KlineQuotaParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._with_details = False

    @property
    def with_details(self):
        return self._with_details

    @with_details.setter
    def with_details(self, value):
        self._with_details = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.with_details is not None:
            params['with_details'] = self.with_details
        return params
    
