# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.model import BaseParams


class AccountsParams(BaseParams):
    def __init__(self):
        super(AccountsParams, self).__init__()
        self._account = None
        self._secret_key = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        return params


class AssetParams(BaseParams):
    def __init__(self):
        super(AssetParams, self).__init__()
        self._account = None
        self._secret_key = None
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
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

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

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.segment:
            params['segment'] = self.segment

        if self.market_value:
            params['market_value'] = self.market_value

        if self.sub_accounts:
            params['sub_accounts'] = self.sub_accounts

        return params


class PositionParams(BaseParams):
    def __init__(self):
        super(PositionParams, self).__init__()
        self._account = None
        self._secret_key = None
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
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

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

        if self.secret_key:
            params['secret_key'] = self.secret_key

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


class ContractParams(BaseParams):
    def __init__(self):
        super(ContractParams, self).__init__()
        self._account = None
        self._secret_key = None
        self._symbol = None
        self._symbols = None
        self._sec_type = None
        self._currency = None
        self._exchange = None
        self._expiry = None
        self._strike = None
        self._right = None
        self._lang = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def symbols(self):
        return self._symbols

    @symbols.setter
    def symbols(self, value):
        self._symbols = value

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
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

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

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.symbol:
            params['symbol'] = self.symbol

        if self.symbols:
            params['symbols'] = self.symbols

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.currency:
            params['currency'] = self.currency

        if self.exchange:
            params['exchange'] = self.exchange

        if self.expiry:
            params['expiry'] = self.expiry

        if self.strike:
            params['strike'] = self.strike

        if self.right:
            params['right'] = self.right

        if self.lang:
            params['lang'] = self.lang

        return params


class OrderParams(BaseParams):
    def __init__(self):
        super(OrderParams, self).__init__()
        self._account = None  # 账户
        self._secret_key = None
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
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

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

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.order_id:
            params['order_id'] = self.order_id

        if self.is_brief:
            params['is_brief'] = self.is_brief

        if self.lang:
            params['lang'] = self.lang

        if self.id:
            params['id'] = self.id

        return params


class OrdersParams(BaseParams):
    def __init__(self):
        super(OrdersParams, self).__init__()
        self._account = None  # 账户
        self._secret_key = None
        self._market = None  # 市场
        self._sec_type = None  # 合约类型
        self._symbol = None  # 合约代码
        self._is_brief = None
        self._lang = None  # 语言
        self._start_date = None
        self._end_date = None
        self._limit = None
        self._states = None
        self._parent_id = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

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

    @property
    def states(self):
        return self._states

    @states.setter
    def states(self, value):
        self._states = value

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._parent_id = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.secret_key:
            params['secret_key'] = self.secret_key

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

        if self.states:
            params['states'] = self.states

        if self.parent_id:
            params['parent_id'] = self.parent_id

        return params


class TransactionsParams(BaseParams):
    def __init__(self):
        super(TransactionsParams, self).__init__()
        self._account = None
        self._secret_key = None
        self._order_id = None
        self._sec_type = None
        self._symbol = None
        self._expiry = None
        self._strike = None
        self._right = None
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
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, value):
        self._order_id = value

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
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

    def to_openapi_dict(self):
        params = dict()
        if self.account:
            params['account'] = self.account

        if self.order_id:
            params['order_id'] = self.order_id

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.symbol:
            params['symbol'] = self.symbol

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.start_date:
            params['start_date'] = self.start_date

        if self.end_date:
            params['end_date'] = self.end_date

        if self.limit:
            params['limit'] = self.limit

        if self.expiry:
            params['expiry'] = self.expiry

        if self.strike:
            params['strike'] = self.strike

        if self.right:
            params['right'] = self.right

        return params


class PlaceModifyOrderParams(BaseParams):
    def __init__(self):
        super(PlaceModifyOrderParams, self).__init__()
        self.account = None
        self.secret_key = None
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
        self.order_legs = None
        self.algo_params = None
        self.adjust_limit = None
        self.user_mark = None

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
            if self.contract.put_call is not None:
                params['right'] = self.contract.put_call
            if self.contract.multiplier is not None:
                params['multiplier'] = self.contract.multiplier

            if self.account:
                params['account'] = self.account
            if self.secret_key:
                params['secret_key'] = self.secret_key

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
            if self.adjust_limit is not None:
                params['adjust_limit'] = self.adjust_limit
            if self.user_mark is not None:
                params['user_mark'] = self.user_mark

            if self.order_legs:
                if len(self.order_legs) > 2:
                    raise Exception('2 order legs at most')
                leg_types = set()
                for order_leg in self.order_legs:
                    if order_leg.leg_type == 'PROFIT':
                        leg_types.add('PROFIT')
                        params['attach_type'] = 'PROFIT'
                        if order_leg.price is not None:
                            params['profit_taker_price'] = order_leg.price
                        if order_leg.time_in_force is not None:
                            params['profit_taker_tif'] = order_leg.time_in_force
                        if order_leg.outside_rth is not None:
                            params['profit_taker_rth'] = order_leg.outside_rth
                    if order_leg.leg_type == 'LOSS':
                        leg_types.add('LOSS')
                        params['attach_type'] = 'LOSS'
                        if order_leg.price is not None:
                            params['stop_loss_price'] = order_leg.price
                        if order_leg.time_in_force is not None:
                            params['stop_loss_tif'] = order_leg.time_in_force
                        if order_leg.outside_rth is not None:
                            params['stop_loss_rth'] = order_leg.outside_rth
                # 括号订单(止盈和止损)
                if len(leg_types) == 2:
                    params['attach_type'] = 'BRACKETS'

            if self.algo_params:
                params['algo_params'] = [{'tag': item[0], 'value': item[1]} for item in self.algo_params.to_dict().items()]
        return params


class CancelOrderParams(BaseParams):
    def __init__(self):
        super(CancelOrderParams, self).__init__()
        self._account = None
        self._secret_key = None
        self._id = None
        self._order_id = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

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

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.order_id:
            params['order_id'] = self.order_id

        if self.id:
            params['id'] = self.id

        return params
