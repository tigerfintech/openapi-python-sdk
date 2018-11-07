# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json
import six
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.order import Order, ORDER_STATUS
from tigeropen.trade.response import CONTRACT_FIELDS

ORDER_FIELD_MAPPINGS = {'parentId': 'parent_id', 'orderId': 'order_id', 'orderType': 'order_type',
    'limitPrice': 'limit_price', 'auxPrice': 'aux_price', 'avgFillPrice': 'avg_fill_price',
    'totalQuantity': 'quantity', 'filledQuantity': 'filled', 'lastFillPrice': 'last_fill_price',
    'orderType': 'order_type', 'realizedPnl': 'realized_pnl', 'secType': 'sec_type', 'remark':'reason',
    'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol', 'outsideRth': 'outside_rth',
    'timeInForce': 'time_in_force', 'openTime': 'order_time', 'latestTime': 'trade_time', 'contractId': 'contract_id',
    'trailStopPrice': 'trail_stop_price', 'trailingPercent': 'trailing_percent', 'percentOffset': 'percent_offset'}


class OrdersResponse(TigerResponse):
    def __init__(self):
        super(OrdersResponse, self).__init__()
        self.orders = []
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(OrdersResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    contract_fields = {}
                    order_fields = {}
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
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
                    right = contract_fields.get('right')
                    multiplier = contract_fields.get('multiplier')
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type, exchange=exchange,
                                        origin_symbol=origin_symbol, local_symbol=local_symbol, expiry=expiry,
                                        strike=strike, right=right, multiplier=multiplier)
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
                    id = order_fields.get('id')
                    order_id = order_fields.get('order_id')
                    parent_id = order_fields.get('parent_id')
                    status = self.get_status(order_fields.get('status'))
                    
                    order = Order(account, contract, action, order_type, quantity, limit_price=limit_price, aux_price=aux_price,
                                  trail_stop_price=trail_stop_price, trailing_percent=trailing_percent,
                                  percent_offset=percent_offset, time_in_force=time_in_force, outside_rth=outside_rth,
                                  filled=filled, avg_fill_price=avg_fill_price, commission=commission,
                                  realized_pnl=realized_pnl, id=id, order_id=order_id, parent_id=parent_id)
                    if 'order_time' in order_fields:
                        order.order_time = order_fields.get('order_time')
                    if 'trade_time' in order_fields:
                        order.trade_time = order_fields.get('trade_time')
                    order.status = status
                    self.orders.append(order)
    
    @staticmethod
    def get_status(value):
        """
        Invalid(-2), Initial(-1), PendingCancel(3), Cancelled(4), Submitted(5), Filled(6), Inactive(7), PendingSubmit(8)
        :param value:
        :return:
        """
        if value == -1:
            return ORDER_STATUS.NEW
        elif value == 2 or value == 8:
            return ORDER_STATUS.HELD
        elif value == 3:
            return ORDER_STATUS.PENDING_CANCEL
        elif value == 4:
            return ORDER_STATUS.CANCELLED
        elif value == 5:
            return ORDER_STATUS.HELD
        elif value == 6:
            return ORDER_STATUS.FILLED
        elif value == 7:
            return ORDER_STATUS.REJECTED
        elif value == -2:
            return ORDER_STATUS.EXPIRED
        
        return ORDER_STATUS.PENDING_NEW
