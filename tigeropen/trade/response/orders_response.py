# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.order_utils import get_order_status
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order, AlgoParams
from tigeropen.trade.response import CONTRACT_FIELDS

ORDER_FIELD_MAPPINGS = {'parentId': 'parent_id', 'orderId': 'order_id', 'orderType': 'order_type',
                        'limitPrice': 'limit_price', 'auxPrice': 'aux_price', 'avgFillPrice': 'avg_fill_price',
                        'totalQuantity': 'quantity', 'filledQuantity': 'filled', 'lastFillPrice': 'last_fill_price',
                        'realizedPnl': 'realized_pnl', 'secType': 'sec_type',
                        'remark': 'reason',
                        'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol', 'outsideRth': 'outside_rth',
                        'timeInForce': 'time_in_force', 'openTime': 'order_time', 'latestTime': 'trade_time',
                        'contractId': 'contract_id', 'algoStrategy': 'algo_strategy',
                        'trailStopPrice': 'trail_stop_price', 'trailingPercent': 'trailing_percent',
                        'percentOffset': 'percent_offset', 'identifier': 'identifier', 'algoParameters': 'algo_params',
                        'userMark': 'user_mark'
                        }


class OrdersResponse(TigerResponse):
    def __init__(self):
        super(OrdersResponse, self).__init__()
        self.orders = []
        self._is_success = None

    def parse_response_content(self, response_content, secret_key=None):
        response = super(OrdersResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    order = OrdersResponse.parse_order(item, secret_key)
                    if order:
                        self.orders.append(order)
            elif 'symbol' in data_json:
                order = OrdersResponse.parse_order(data_json, secret_key)
                if order:
                    self.orders.append(order)

    @staticmethod
    def parse_order(item, secret_key=None):
        contract_fields = {}
        order_fields = {}
        for key, value in item.items():
            if value is None:
                continue
            tag = ORDER_FIELD_MAPPINGS[key] if key in ORDER_FIELD_MAPPINGS else key
            if tag in CONTRACT_FIELDS:
                contract_fields[tag] = value
            else:
                order_fields[tag] = value

        contract_id = contract_fields.get('contract_id')
        symbol = contract_fields.get('symbol')
        currency = contract_fields.get('currency')
        sec_type = contract_fields.get('sec_type')
        exchange = contract_fields.get('exchange')
        origin_symbol = contract_fields.get('origin_symbol')
        local_symbol = contract_fields.get('local_symbol')
        expiry = contract_fields.get('expiry')
        strike = contract_fields.get('strike')
        put_call = contract_fields.get('right')
        multiplier = contract_fields.get('multiplier')
        identifier = contract_fields.get('identifier')
        contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type, exchange=exchange,
                            origin_symbol=origin_symbol, local_symbol=local_symbol, expiry=expiry,
                            strike=strike, put_call=put_call, multiplier=multiplier, identifier=identifier)
        account = order_fields.get('account')
        action = order_fields.get('action')
        order_type = order_fields.get('order_type')
        quantity = order_fields.get('quantity')
        limit_price = order_fields.get('limit_price')
        aux_price = order_fields.get('aux_price')
        trail_stop_price = order_fields.get('trail_stop_price')
        trailing_percent = order_fields.get('trailing_percent')
        percent_offset = order_fields.get('percent_offset')
        time_in_force = order_fields.get('time_in_force')
        outside_rth = order_fields.get('outside_rth')
        filled = order_fields.get('filled')
        avg_fill_price = order_fields.get('avg_fill_price')
        commission = order_fields.get('commission')
        realized_pnl = order_fields.get('realized_pnl')
        id_ = order_fields.get('id')
        order_id = order_fields.get('order_id')
        parent_id = order_fields.get('parent_id')
        status = get_order_status(order_fields.get('status'))
        algo_params = AlgoParams.from_tags(order_fields.get('algo_params'))
        liquidation = order_fields.get('liquidation')
        algo_strategy = order_fields.get('algo_strategy')
        discount = order_fields.get('discount')
        attr_desc = order_fields.get('attr_desc')
        source = order_fields.get('source')
        user_mark = order_fields.get('user_mark')

        order = Order(account, contract, action, order_type, quantity, limit_price=limit_price, aux_price=aux_price,
                      trail_stop_price=trail_stop_price, trailing_percent=trailing_percent,
                      percent_offset=percent_offset, time_in_force=time_in_force, outside_rth=outside_rth,
                      filled=filled, avg_fill_price=avg_fill_price, commission=commission,
                      realized_pnl=realized_pnl, id=id_, order_id=order_id, parent_id=parent_id,
                      algo_params=algo_params, liquidation=liquidation, algo_strategy=algo_strategy, discount=discount,
                      attr_desc=attr_desc, source=source, user_mark=user_mark)
        if 'order_time' in order_fields:
            order.order_time = order_fields.get('order_time')
        if 'trade_time' in order_fields:
            order.trade_time = order_fields.get('trade_time')
        if 'reason' in order_fields:
            order.reason = order_fields.get('reason')
        if secret_key is not None:
            order.secret_key = secret_key
        order.status = status

        return order

