# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.domain.position import Position, TradableQuantityItem
from tigeropen.trade.response import CONTRACT_FIELDS

POSITION_FIELD_MAPPINGS = {'position': 'quantity', 'latestPrice': 'market_price'}


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
            if 'items' in self.data:
                for item in self.data['items']:

                    contract_fields = {}
                    position_fields = {}
                    for key, value in item.items():
                        if value is None:
                            continue
                        tag = POSITION_FIELD_MAPPINGS[key] if key in POSITION_FIELD_MAPPINGS else string_utils.camel_to_underline(key)
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
                    put_call = contract_fields.get('right')
                    multiplier = contract_fields.get('multiplier')
                    identifier = contract_fields.get('identifier')
                    market = contract_fields.get('market')
                    categories = contract_fields.get('categories')
                    name = contract_fields.get('name')
                    underlying_contract_name = contract_fields.get('underlying_contract_name')
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type,
                                        exchange=exchange, origin_symbol=origin_symbol, local_symbol=local_symbol,
                                        expiry=expiry, strike=strike, put_call=put_call, multiplier=multiplier,
                                        identifier=identifier, market=market, categories=categories, name=name,
                                        underlying_contract_name=underlying_contract_name)
                    position = Position(contract=contract, **position_fields)
                    self.positions.append(position)


class EstimateTradableQuantityResponse(TigerResponse):
    def __init__(self):
        super(EstimateTradableQuantityResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(EstimateTradableQuantityResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.result = TradableQuantityItem(**string_utils.camel_to_underline_obj(self.data))
