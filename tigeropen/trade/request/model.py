# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""


class AccountsParams(object):
    def __init__(self):
        self._account = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        return params


class AssetParams(object):
    def __init__(self):
        self._account = None
        self._segment = False
        self._market_value = False
        self._sub_accounts = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def segment(self):
        return self._segment

    @segment.setter
    def segment(self, value):
        self._segment = value

    @property
    def market_value(self):
        return self._market_value

    @market_value.setter
    def market_value(self, value):
        self._market_value = value

    @property
    def sub_accounts(self):
        return self._sub_accounts

    @sub_accounts.setter
    def sub_accounts(self, value):
        self._sub_accounts = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.segment:
            params['segment'] = self.segment

        if self.market_value:
            params['market_value'] = self.market_value

        if self.sub_accounts:
            params['sub_accounts'] = self.sub_accounts

        return params


class PositionParams(object):
    def __init__(self):
        self._account = None
        self._symbol = None
        self._sec_type = None
        self._currency = None
        self._market = None
        self._sub_accounts = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def sec_type(self):
        return self._sec_type

    @sec_type.setter
    def sec_type(self, value):
        self._sec_type = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def market(self):
        return self._market

    @market.setter
    def market(self, value):
        self._market = value

    @property
    def sub_accounts(self):
        return self._sub_accounts

    @sub_accounts.setter
    def sub_accounts(self, value):
        self._sub_accounts = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.symbol:
            params['symbol'] = self.symbol

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.currency:
            params['currency'] = self.currency

        if self.market:
            params['market'] = self.market

        if self.sub_accounts:
            params['sub_accounts'] = self.sub_accounts

        return params


class ContractParams(object):
    def __init__(self):
        self._account = None
        self._contract_id = None
        self._symbol = None
        self._sec_type = None
        self._currency = None
        self._exchange = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def contract_id(self):
        return self._contract_id

    @contract_id.setter
    def contract_id(self, value):
        self._contract_id = value

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def sec_type(self):
        return self._sec_type

    @sec_type.setter
    def sec_type(self, value):
        self._sec_type = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def exchange(self):
        return self._exchange

    @exchange.setter
    def exchange(self, value):
        self._exchange = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.symbol:
            params['symbol'] = self.symbol

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.currency:
            params['currency'] = self.currency

        if self.exchange:
            params['exchange'] = self.exchange

        return params


class OrderParams(object):
    def __init__(self):
        self._account = None  # 账户
        self._id = None  # 订单号(全局)
        self._order_id = None  # 订单号(账户维度)
        self._is_brief = None
        self._lang = None  # 语言

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, value):
        self._order_id = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def is_brief(self):
        return self._is_brief

    @is_brief.setter
    def is_brief(self, value):
        self._is_brief = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.order_id:
            params['order_id'] = self.order_id

        if self.is_brief:
            params['is_brief'] = self.is_brief

        if self.lang:
            params['lang'] = self.lang

        return params


class OrdersParams(object):
    def __init__(self):
        self._account = None  # 账户
        self._market = None  # 市场
        self._sec_type = None  # 合约类型
        self._symbol = None  # 合约代码
        self._is_brief = None
        self._lang = None  # 语言
        self._start_date = None
        self._end_date = None
        self._limit = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

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
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    @property
    def is_brief(self):
        return self._is_brief

    @is_brief.setter
    def is_brief(self, value):
        self._is_brief = value

    @property
    def lang(self):
        return self._lang

    @lang.setter
    def lang(self, value):
        self._lang = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.market:
            params['market'] = self.market

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.symbol:
            params['symbol'] = self.symbol

        if self.start_date:
            params['start_date'] = self.start_date

        if self.end_date:
            params['end_date'] = self.end_date

        if self.limit:
            params['limit'] = self.limit

        if self.is_brief:
            params['is_brief'] = self.is_brief

        if self.lang:
            params['lang'] = self.lang

        return params


class PlaceModifyOrderParams(object):
    def __init__(self):
        self.account = None
        self.id = None
        self.order_id = None
        self.contract = None
        self.action = None
        self.order_type = None
        self.quantity = None
        self.limit_price = None
        self.aux_price = None
        self.trail_stop_price = None
        self.trailing_percent = None
        self.percent_offset = None
        self.time_in_force = None
        self.outside_rth = None

    def to_openapi_dict(self):
        params = dict()

        if self.contract:
            if self.contract.symbol is not None:
                params['symbol'] = self.contract.symbol
            if self.contract.currency is not None:
                params['currency'] = self.contract.currency
            if self.contract.sec_type is not None:
                params['sec_type'] = self.contract.sec_type
            if self.contract.exchange is not None:
                params['exchange'] = self.contract.exchange
            if self.contract.local_symbol is not None:
                params['local_symbol'] = self.contract.local_symbol
            if self.contract.expiry is not None:
                params['expiry'] = self.contract.expiry
            if self.contract.strike is not None:
                params['strike'] = self.contract.strike
            if self.contract.right is not None:
                params['right'] = self.contract.right
            if self.contract.multiplier is not None:
                params['multiplier'] = self.contract.multiplier

            if self.account:
                params['account'] = self.account

            if self.order_id:
                params['order_id'] = self.order_id
            if self.id:
                params['id'] = self.id
            if self.order_type:
                params['order_type'] = self.order_type
            if self.action:
                params['action'] = self.action
            if self.quantity is not None:
                params['total_quantity'] = self.quantity
            if self.limit_price is not None:
                params['limit_price'] = self.limit_price
            if self.aux_price is not None:
                params['aux_price'] = self.aux_price
            if self.trail_stop_price is not None:
                params['trail_stop_price'] = self.trail_stop_price
            if self.trailing_percent is not None:
                params['trailing_percent'] = self.trailing_percent
            if self.percent_offset is not None:
                params['percent_offset'] = self.percent_offset
            if self.time_in_force is not None:
                params['time_in_force'] = self.time_in_force
            if self.outside_rth is not None:
                params['outside_rth'] = self.outside_rth

        return params


class CancelOrderParams(object):
    def __init__(self):
        self._account = None
        self._id = None
        self._order_id = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, value):
        self._order_id = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.order_id:
            params['order_id'] = self.order_id

        if self.id:
            params['id'] = self.id

        return params
