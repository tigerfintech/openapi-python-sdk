# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.consts import OrderType, SecurityType
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
        params = super().to_openapi_dict()
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
        self._base_currency = None
        self._consolidated = None

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

    @property
    def base_currency(self):
        return self._base_currency

    @base_currency.setter
    def base_currency(self, value):
        self._base_currency = value

    @property
    def consolidated(self):
        return self._consolidated

    @consolidated.setter
    def consolidated(self, value):
        self._consolidated = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
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

        if self.base_currency:
            params['base_currency'] = self.base_currency

        if self.consolidated is not None:
            params['consolidated'] = self.consolidated

        return params

class AggregateAssetParams(BaseParams):
    def __init__(self):
        super(AggregateAssetParams, self).__init__()
        self._account = None
        self._secret_key = None
        self._seg_type = False
        self._base_currency = None

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
    def seg_type(self):
        return self._seg_type
    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value
    @property
    def base_currency(self):
        return self._base_currency
    @base_currency.setter
    def base_currency(self, value):
        self._base_currency = value 

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        if self.seg_type:
            params['seg_type'] = self.seg_type
        if self.base_currency:
            params['base_currency'] = self.base_currency
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
        self._expiry = None
        self._strike = None
        self._right = None
        self._asset_quote_type = None

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
    def asset_quote_type(self):
        return self._asset_quote_type

    @asset_quote_type.setter
    def asset_quote_type(self, value):
        self._asset_quote_type = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
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

        if self.expiry:
            params['expiry'] = self.expiry

        if self.strike:
            params['strike'] = self.strike

        if self.right:
            params['right'] = self.right

        if self.asset_quote_type:
            params['asset_quote_type'] = self.asset_quote_type

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

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
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

        return params


class OrderParams(BaseParams):
    def __init__(self):
        super(OrderParams, self).__init__()
        self._account = None  # 账户
        self._secret_key = None
        self._id = None  # 订单号(全局)
        self._order_id = None  # 订单号(账户维度)
        self._is_brief = None
        self._show_charges = None

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
    def show_charges(self):
        return self._show_charges

    @show_charges.setter
    def show_charges(self, value):
        self._show_charges = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.order_id:
            params['order_id'] = self.order_id

        if self.is_brief:
            params['is_brief'] = self.is_brief

        if self.id:
            params['id'] = self.id

        if self.show_charges is not None:
            params['show_charges'] = self.show_charges

        return params


class OrdersParams(BaseParams):
    def __init__(self):
        super(OrdersParams, self).__init__()
        self._account = None  # 账户
        self._secret_key = None
        self._market = None  # 市场
        self._sec_type = None  # 合约类型
        self._seg_type = None  # segment type
        self._symbol = None  # 合约代码
        self._is_brief = None
        self._start_date = None
        self._end_date = None
        self._limit = None
        self._states = None
        self._parent_id = None
        self._sort_by = None
        self._show_charges = None
        self._page_token = None

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
    def seg_type(self):
        return self._seg_type

    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value

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

    @property
    def sort_by(self):
        return self._sort_by

    @sort_by.setter
    def sort_by(self, value):
        self._sort_by = value

    @property
    def show_charges(self):
        return self._show_charges

    @show_charges.setter
    def show_charges(self, value):
        self._show_charges = value

    @property
    def page_token(self):
        return self._page_token

    @page_token.setter
    def page_token(self, value):
        self._page_token = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.market:
            params['market'] = self.market

        if self.sec_type:
            params['sec_type'] = self.sec_type

        if self.seg_type:
            params['seg_type'] = self.seg_type

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

        if self.states:
            params['states'] = self.states

        if self.parent_id:
            params['parent_id'] = self.parent_id

        if self.sort_by:
            params['sort_by'] = self.sort_by

        if self.show_charges is not None:
            params['show_charges'] = self.show_charges

        if self.page_token:
            params['page_token'] = self.page_token

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
        self._page_token = None

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

    @property
    def page_token(self):
        return self._page_token

    @page_token.setter
    def page_token(self, value):
        self._page_token = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
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

        if self.page_token:
            params['page_token'] = self.page_token

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
        self.quantity_scale = None
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
        self.expire_time = None
        self.combo_type = None
        self.contract_legs = None
        self.total_cash_amount = None
        self.oca_orders = None
        self.trading_session_type = None

    def _parse_contract_param(self):
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

        if self.contract_legs:
            params['contract_legs'] = list()
            for item in self.contract_legs:
                params['contract_legs'].append(item.to_openapi_dict())
            params['sec_type'] = SecurityType.MLEG.value

        return params
               
    def _parse_account_param(self):
        params = dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        return params

    def _parse_common_param(self):
        params = dict()
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
        if self.quantity_scale is not None:
            params['total_quantity_scale'] = self.quantity_scale
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
        if self.expire_time is not None:
            params['expire_time'] = self.expire_time
        if self.total_cash_amount is not None:
            params['cash_amount'] = self.total_cash_amount
        if self.algo_params:
            params['algo_params'] = [{'tag': item[0], 'value': item[1]} for item in self.algo_params.to_dict().items()]
        if self.combo_type:
            params['combo_type'] = self.combo_type
        if self.trading_session_type:
            params['trading_session_type'] = self.trading_session_type
        return params

    def _parse_leg_param(self):
        params = dict()
        if self.order_legs:
            leg_types = set()
            for order_leg in self.order_legs:
                if order_leg.leg_type == 'PROFIT':
                    leg_types.add(order_leg.leg_type)
                    params['attach_type'] = order_leg.leg_type
                    if order_leg.price is not None:
                        params['profit_taker_price'] = order_leg.price
                    if order_leg.time_in_force is not None:
                        params['profit_taker_tif'] = order_leg.time_in_force
                    if order_leg.outside_rth is not None:
                        params['profit_taker_rth'] = order_leg.outside_rth
                elif order_leg.leg_type == 'LOSS':
                    leg_types.add(order_leg.leg_type)
                    params['attach_type'] = order_leg.leg_type
                    if order_leg.price is not None:
                        params['stop_loss_price'] = order_leg.price
                    if order_leg.time_in_force is not None:
                        params['stop_loss_tif'] = order_leg.time_in_force
                    if order_leg.outside_rth is not None:
                        params['stop_loss_rth'] = order_leg.outside_rth
                    if order_leg.limit_price is not None:
                        params['stop_loss_limit_price'] = order_leg.limit_price
                    if order_leg.trailing_percent is not None:
                        params['stop_loss_trailing_percent'] = order_leg.trailing_percent
                    if order_leg.trailing_amount is not None:
                        params['stop_loss_trailing_amount'] = order_leg.trailing_amount

            # 括号订单(止盈和止损)
            if len(leg_types) == 2 and ('LOSS' in leg_types or 'PROFIT' in leg_types):
                params['attach_type'] = 'BRACKETS'
        return params

    def _parse_oca_param(self):
        params = dict()
        contract_params = self._parse_contract_param()
        params['oca_orders'] = list()
        account_params = self._parse_account_param()
        if self.order_legs:
            for order_leg in self.order_legs:
                if order_leg.leg_type in ('LMT', 'STP', 'STP_LMT'):
                    # OCA 订单
                    oca_params = dict()
                    oca_params.update(contract_params)
                    oca_params.update(account_params)
                    oca_params['order_type'] = order_leg.leg_type
                    oca_params['action'] = self.action
                    oca_params['total_quantity'] = order_leg.quantity if order_leg.quantity else self.quantity
                    if order_leg.price is not None and order_leg.leg_type != 'LMT':
                        oca_params['aux_price'] = order_leg.price
                    if order_leg.leg_type in ('LMT', 'STP_LMT'):
                        oca_params['limit_price'] = order_leg.limit_price if order_leg.limit_price else order_leg.price
                    if order_leg.time_in_force is not None:
                        oca_params['time_in_force'] = order_leg.time_in_force
                    if order_leg.outside_rth is not None:
                        oca_params['outside_rth'] = order_leg.outside_rth
                    params['oca_orders'].append(oca_params)
        return params

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        common_params = self._parse_common_param()

        if self.order_type and self.order_type == OrderType.OCA.value:
            params.update(self._parse_account_param())
            params.update(self._parse_oca_param())
            params.update(common_params)
            params.pop('order_type', None)
            params.pop('action', None)
            params.pop('total_quantity', None)
        else:
            params.update(self._parse_account_param())
            params.update(self._parse_contract_param())
            params.update(common_params)
            params.update(self._parse_leg_param())
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
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.order_id:
            params['order_id'] = self.order_id

        if self.id:
            params['id'] = self.id

        return params


class AnalyticsAssetParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._account = None
        self._sub_account = None
        self._secret_key = None
        self._seg_type = None
        self._currency = None
        self._sub_accounts = None
        self._start_date = None
        self._end_date = None

    @property
    def account(self):
        return self._account

    @account.setter
    def account(self, value):
        self._account = value

    @property
    def sub_account(self):
        return self._sub_account

    @sub_account.setter
    def sub_account(self, value):
        self._sub_account = value

    @property
    def secret_key(self):
        return self._secret_key

    @secret_key.setter
    def secret_key(self, value):
        self._secret_key = value

    @property
    def seg_type(self):
        return self._seg_type

    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def sub_accounts(self):
        return self._sub_accounts

    @sub_accounts.setter
    def sub_accounts(self, value):
        self._sub_accounts = value

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

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account

        if self.sub_account:
            params['sub_account'] = self.sub_account

        if self.secret_key:
            params['secret_key'] = self.secret_key

        if self.seg_type:
            params['seg_type'] = self.seg_type

        if self.currency:
            params['currency'] = self.currency

        if self.sub_accounts:
            params['sub_accounts'] = self.sub_accounts

        if self.start_date:
            params['start_date'] = self.start_date

        if self.end_date:
            params['end_date'] = self.end_date
        return params


class SegmentFundParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._id = None
        self._account = None
        self._secret_key = None
        self._from_segment = None
        self._to_segment = None
        self._currency = None
        self._amount = None
        self._limit = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

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
    def from_segment(self):
        return self._from_segment

    @from_segment.setter
    def from_segment(self, value):
        self._from_segment = value

    @property
    def to_segment(self):
        return self._to_segment

    @to_segment.setter
    def to_segment(self, value):
        self._to_segment = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self._id:
            params['id'] = self._id
        if self._account:
            params['account'] = self._account
        if self._secret_key:
            params['secret_key'] = self._secret_key
        if self._from_segment:
            params['from_segment'] = self._from_segment
        if self._to_segment:
            params['to_segment'] = self._to_segment
        if self._currency:
            params['currency'] = self._currency
        if self._amount:
            params['amount'] = self._amount
        if self._limit:
            params['limit'] = self._limit
        return params


class ForexTradeOrderParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._account = None
        self._secret_key = None
        self._source_currency = None
        self._source_amount = None
        self._target_currency = None
        self._seg_type = None
        self._external_id = None
        self._time_in_force = None

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
    def source_currency(self):
        return self._source_currency

    @source_currency.setter
    def source_currency(self, value):
        self._source_currency = value

    @property
    def source_amount(self):
        return self._source_amount

    @source_amount.setter
    def source_amount(self, value):
        self._source_amount = value

    @property
    def target_currency(self):
        return self._target_currency

    @target_currency.setter
    def target_currency(self, value):
        self._target_currency = value

    @property
    def seg_type(self):
        return self._seg_type

    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value

    @property
    def external_id(self):
        return self._external_id

    @external_id.setter
    def external_id(self, value):
        self._external_id = value

    @property
    def time_in_force(self):
        return self._time_in_force

    @time_in_force.setter
    def time_in_force(self, value):
        self._time_in_force = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        if self.source_currency:
            params['source_currency'] = self.source_currency
        if self.source_amount:
            params['source_amount'] = self.source_amount
        if self.target_currency:
            params['target_currency'] = self.target_currency
        if self.seg_type:
            params['seg_type'] = self.seg_type
        if self.external_id:
            params['external_id'] = self.external_id
        if self.time_in_force:
            params['time_in_force'] = self.time_in_force
        return params


class EstimateTradableQuantityModel(BaseParams):
    def __init__(self):
        super().__init__()
        self._account = None
        self._secret_key = None
        self._contract = None
        self._seg_type = None
        self._action = None
        self._order_type = None
        self._limit_price = None
        self._stop_price = None

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
    def contract(self):
        return self._contract

    @contract.setter
    def contract(self, value):
        self._contract = value

    @property
    def seg_type(self):
        return self._seg_type

    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        self._action = value

    @property
    def order_type(self):
        return self._order_type

    @order_type.setter
    def order_type(self, value):
        self._order_type = value

    @property
    def limit_price(self):
        return self._limit_price

    @limit_price.setter
    def limit_price(self, value):
        self._limit_price = value

    @property
    def stop_price(self):
        return self._stop_price

    @stop_price.setter
    def stop_price(self, value):
        self._stop_price = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        if self.contract:
            if self.contract.symbol:
                params['symbol'] = self.contract.symbol
            if self.contract.expiry:
                params['expiry'] = self.contract.expiry
            if self.contract.strike:
                params['strike'] = self.contract.strike
            if self.contract.put_call:
                params['right'] = self.contract.put_call
            if self.contract.sec_type:
                params['sec_type'] = self.contract.sec_type
        if self.seg_type:
            params['seg_type'] = self.seg_type
        if self.action:
            params['action'] = self.action
        if self.order_type:
            params['order_type'] = self.order_type
        if self.limit_price:
            params['limit_price'] = self.limit_price
        if self.stop_price:
            params['stop_price'] = self.stop_price
        return params

class FundingHistoryParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._account = None
        self._secret_key = None
        self._seg_type = None

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
    def seg_type(self):
        return self._seg_type

    @seg_type.setter
    def seg_type(self, value):
        self._seg_type = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        if self.seg_type:
            params['seg_type'] = self.seg_type
        return params

class FundDetailsParams(BaseParams):
    def __init__(self):
        super().__init__()
        self._account = None
        self._secret_key = None
        self._seg_types = None
        self._fund_type = None
        self._currency = None
        self._start_date = None
        self._end_date = None
        self._start = None
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
    def seg_types(self):
        return self._seg_types

    @seg_types.setter
    def seg_types(self, value):
        self._seg_types = value

    @property
    def fund_type(self):
        return self._fund_type

    @fund_type.setter
    def fund_type(self, value):
        self._fund_type = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        self._currency = value

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
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, value):
        self._limit = value

    def to_openapi_dict(self):
        params = super().to_openapi_dict()
        if self.account:
            params['account'] = self.account
        if self.secret_key:
            params['secret_key'] = self.secret_key
        if self.seg_types:
            params['seg_types'] = self.seg_types
        if self.fund_type:
            params['fund_type'] = self.fund_type
        if self.currency:
            params['currency'] = self.currency
        if self.start_date:
            params['start_date'] = self.start_date
        if self.end_date:
            params['end_date'] = self.end_date
        if self._start is not None:
            params['start'] = self._start
        if self._limit:
            params['limit'] = self._limit
        return params
