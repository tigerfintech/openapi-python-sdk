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
from tigeropen.trade.domain.position import Position
from tigeropen.trade.response import CONTRACT_FIELDS

POSITION_FIELD_MAPPINGS = {'averageCost': 'average_cost', 'position': 'quantity', 'latestPrice': 'market_price',
    'marketValue': 'market_value', 'orderType': 'order_type', 'realizedPnl': 'realized_pnl',
    'unrealizedPnl': 'unrealized_pnl', 'secType': 'sec_type', 'localSymbol': 'local_symbol',
    'originSymbol': 'origin_symbol', 'contractId':'contract_id'}


class PositionsResponse(TigerResponse):
    def __init__(self):
        super(PositionsResponse, self).__init__()
        self.positions = []
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(PositionsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    contract_fields = {}
                    position_fields = {}
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
                        tag = POSITION_FIELD_MAPPINGS[key] if key in POSITION_FIELD_MAPPINGS else key
                        if tag in CONTRACT_FIELDS:
                            contract_fields[tag] = value
                        else:
                            position_fields[tag] = value
                    
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
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type,
                                        exchange=exchange, origin_symbol=origin_symbol, local_symbol=local_symbol,
                                        expiry=expiry, strike=strike, right=right, multiplier=multiplier)
                    account = position_fields.get('account')
                    quantity = position_fields.get('quantity')
                    average_cost = position_fields.get('average_cost')
                    market_price = position_fields.get('market_price')
                    market_value = position_fields.get('market_value')
                    realized_pnl = position_fields.get('realized_pnl')
                    unrealized_pnl = position_fields.get('unrealized_pnl')
                    
                    position = Position(account, contract, quantity, average_cost=average_cost,
                                        market_price=market_price, market_value=market_value,
                                        realized_pnl=realized_pnl, unrealized_pnl=unrealized_pnl)
                    self.positions.append(position)
