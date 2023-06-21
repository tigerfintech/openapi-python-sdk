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

POSITION_FIELD_MAPPINGS = {'averageCost': 'average_cost', 'position': 'quantity', 'latestPrice': 'market_price',
                           'marketValue': 'market_value', 'orderType': 'order_type', 'realizedPnl': 'realized_pnl',
                           'unrealizedPnl': 'unrealized_pnl', 'secType': 'sec_type', 'localSymbol': 'local_symbol',
                           'originSymbol': 'origin_symbol', 'contractId': 'contract_id', 'identifier': 'identifier',
                           'salable': 'saleable', 'positionScale': 'position_scale',
                           'averageCostByAverage': 'average_cost_by_average',
                           'unrealizedPnlByAverage': 'unrealized_pnl_by_average',
                           'realizedPnlByAverage': 'realized_pnl_by_average',
                           'unrealizedPnlPercent': 'unrealized_pnl_percent',
                           'unrealizedPnlPercentByAverage': 'unrealized_pnl_percent_by_average'}


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
                    put_call = contract_fields.get('right')
                    multiplier = contract_fields.get('multiplier')
                    identifier = contract_fields.get('identifier')
                    market = contract_fields.get('market')
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type,
                                        exchange=exchange, origin_symbol=origin_symbol, local_symbol=local_symbol,
                                        expiry=expiry, strike=strike, put_call=put_call, multiplier=multiplier,
                                        identifier=identifier, market=market)
                    account = position_fields.get('account')
                    quantity = position_fields.get('quantity')
                    average_cost = position_fields.get('average_cost')
                    market_price = position_fields.get('market_price')
                    market_value = position_fields.get('market_value')
                    realized_pnl = position_fields.get('realized_pnl')
                    unrealized_pnl = position_fields.get('unrealized_pnl')
                    saleable = position_fields.get('saleable')
                    position_scale = position_fields.get('position_scale')
                    realized_pnl_by_average = position_fields.get('realized_pnl_by_average')
                    unrealized_pnl_by_average = position_fields.get('unrealized_pnl_by_average')
                    average_cost_by_average = position_fields.get('average_cost_by_average')
                    unrealized_pnl_percent = position_fields.get('unrealized_pnl_percent')
                    unrealized_pnl_percent_by_average = position_fields.get('unrealized_pnl_percent_by_average')
                    position = Position(account, contract, quantity, average_cost=average_cost,
                                        market_price=market_price, market_value=market_value,
                                        realized_pnl=realized_pnl, unrealized_pnl=unrealized_pnl,
                                        saleable=saleable, position_scale=position_scale,
                                        realized_pnl_by_average=realized_pnl_by_average,
                                        unrealized_pnl_by_average=unrealized_pnl_by_average,
                                        average_cost_by_average=average_cost_by_average,
                                        unrealized_pnl_percent=unrealized_pnl_percent,
                                        unrealized_pnl_percent_by_average=unrealized_pnl_percent_by_average)
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
