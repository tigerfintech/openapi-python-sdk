# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import THREAD_LOCAL, SecurityType, Market, Currency
from tigeropen.trade.domain.order import Order
from tigeropen.trade.response.account_profile_response import ProfilesResponse

from tigeropen.trade.response.contracts_response import ContractsResponse
from tigeropen.trade.response.order_id_response import OrderIdResponse
from tigeropen.trade.response.orders_response import OrdersResponse
from tigeropen.tiger_open_client import TigerOpenClient, ApiException
from tigeropen.trade.request.model import ContractParams, AccountsParams, AssetParams, PositionParams, OrdersParams, \
    OrderParams, PlaceModifyOrderParams, CancelOrderParams
from tigeropen.quote.request import OpenApiRequest
from tigeropen.trade.response.assets_response import AssetsResponse
from tigeropen.common.consts.service_types import CONTRACT, ACCOUNTS, POSITIONS, ASSETS, ORDERS, ORDER_NO, CANCEL_ORDER, \
    MODIFY_ORDER, PLACE_ORDER

import logging

from tigeropen.trade.response.positions_response import PositionsResponse


class TradeClient(TigerOpenClient):
    def __init__(self, client_config, logger=None):
        if not logger:
            logger = logging.getLogger('tiger_openapi')
        super(TradeClient, self).__init__(client_config, logger=logger)
        if client_config:
            self._account = client_config.account
            self._lang = client_config.language
        else:
            self._account = None

    def get_managed_accounts(self):
        params = AccountsParams()
        params.account = self._account
        request = OpenApiRequest(ACCOUNTS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ProfilesResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.profiles
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_contracts(self, symbol, sec_type=SecurityType.STK, currency=Currency.USD, exchange=None):
        params = ContractParams()
        params.account = self._account
        params.symbol = symbol
        if sec_type:
            params.sec_type = sec_type.value
        if currency:
            params.currency = currency.value
        params.exchange = exchange

        request = OpenApiRequest(CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_contract(self, contract_id):
        params = ContractParams()
        params.account = self._account
        params.contract_id = contract_id

        request = OpenApiRequest(CONTRACT, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = ContractsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.contracts[0] if len(response.contracts) == 1 else None
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_positions(self, sec_type=SecurityType.STK, currency=Currency.ALL, market=Market.ALL, symbol=None,
                      sub_accounts=None):
        params = PositionParams()
        params.account = self._account
        if sec_type:
            params.sec_type = sec_type.value
        params.sub_accounts = sub_accounts
        if currency:
            params.currency = currency.value
        if market:
            params.market = market.value
        params.symbol = symbol

        request = OpenApiRequest(POSITIONS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = PositionsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.positions
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_assets(self, sub_accounts=None, segment=False, market_value=False):
        params = AssetParams()
        params.account = self._account
        params.sub_accounts = sub_accounts
        params.segment = segment
        params.market_value = market_value

        request = OpenApiRequest(ASSETS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = AssetsResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.assets
            else:
                raise ApiException(response.code, response.message)

        return None

    def get_orders(self, sec_type=SecurityType.ALL, market=Market.ALL, symbol=None, start_time=None, end_time=None,
                   limit=100, is_brief=False):
        params = OrdersParams()
        params.account = self._account
        params.sec_type = sec_type.value
        params.market = market.value
        params.symbol = symbol
        params.start_data = start_time
        params.end_date = end_time
        params.limit = limit
        params.is_brief = is_brief
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.orders
            else:
                raise ApiException(response.code, response.message)
        return None

    def get_order(self, id=None, order_id=None, is_brief=False):
        params = OrderParams()
        params.account = self._account
        params.id = id
        params.order_id = order_id
        params.is_brief = is_brief
        request = OpenApiRequest(ORDERS, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrdersResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.orders[0] if len(response.orders) == 1 else None
            else:
                raise ApiException(response.code, response.message)
        return None

    def create_order(self, account, contract, action, order_type, quantity, limit_price=None, aux_price=None,
                     trail_stop_price=None, trailing_percent=None, percent_offset=None, time_in_force=None,
                     outside_rth=None):
        params = AccountsParams()
        params.account = self._account
        request = OpenApiRequest(ORDER_NO, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order_id = response.order_id
                order = Order(account, contract, action, order_type, quantity, limit_price=limit_price,
                              aux_price=aux_price, trail_stop_price=trail_stop_price,
                              trailing_percent=trailing_percent, percent_offset=percent_offset,
                              time_in_force=time_in_force, outside_rth=outside_rth, order_id=order_id)
                return order
            else:
                raise ApiException(response.code, response.message)

        return None

    def place_order(self, order):
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.order_id = order.order_id
        params.quantity = order.quantity
        params.limit_price = order.limit_price
        params.aux_price = order.aux_price
        params.trail_stop_price = order.trail_stop_price
        params.trailing_percent = order.trailing_percent
        params.percent_offset = order.percent_offset
        params.time_in_force = order.time_in_force
        params.outside_rth = order.outside_rth
        request = OpenApiRequest(PLACE_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                order.id = response.id
                return response.order_id == order.order_id if order.order_id else True
            else:
                raise ApiException(response.code, response.message)

        return False

    def modify_order(self, order, quantity=None, limit_price=None, aux_price=None,
                     trail_stop_price=None, trailing_percent=None, percent_offset=None,
                     time_in_force=None, outside_rth=None):
        params = PlaceModifyOrderParams()
        params.account = order.account
        params.order_id = order.order_id
        params.id = order.id
        params.contract = order.contract
        params.action = order.action
        params.order_type = order.order_type
        params.quantity = quantity if quantity is not None else order.quantity
        params.limit_price = limit_price if limit_price is not None else order.limit_price
        params.aux_price = aux_price if aux_price is not None else order.aux_price
        params.trail_stop_price = trail_stop_price if trail_stop_price is not None else order.trail_stop_price
        params.trailing_percent = trailing_percent if trailing_percent is not None else order.trailing_percent
        params.percent_offset = percent_offset if percent_offset is not None else order.percent_offset
        params.time_in_force = time_in_force if time_in_force is not None else order.time_in_force
        params.outside_rth = outside_rth if outside_rth is not None else order.outside_rth
        request = OpenApiRequest(MODIFY_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.order_id == order.order_id if order.order_id else response.id == order.id
            else:
                raise ApiException(response.code, response.message)

        return False

    def cancel_order(self, id=None, order_id=None):
        params = CancelOrderParams()
        params.account = self._account
        params.order_id = order_id
        params.id = id
        request = OpenApiRequest(CANCEL_ORDER, biz_model=params)
        response_content = self.__fetch_data(request)
        if response_content:
            response = OrderIdResponse()
            response.parse_response_content(response_content)
            if response.is_success():
                return response.order_id == order_id if order.order_id else response.id == order.id
            else:
                raise ApiException(response.code, response.message)

        return False

    def __fetch_data(self, request):
        try:
            response = super(TradeClient, self).execute(request)
            return response
        except Exception as e:
            if THREAD_LOCAL.logger:
                THREAD_LOCAL.logger.error(e, exc_info=True)
            raise e
            # print(traceback.format_exc())

        return None
