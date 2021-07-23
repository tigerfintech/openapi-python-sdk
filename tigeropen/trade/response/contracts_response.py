# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json

from tigeropen.common.response import TigerResponse
from tigeropen.trade.domain.contract import Contract
from tigeropen.trade.response import CONTRACT_FIELDS

CONTRACT_FIELD_MAPPINGS = {'secType': 'sec_type', 'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol',
                           'conid': 'contract_id', 'contractId': 'contract_id',
                           'shortMargin': 'short_margin', 'shortFeeRate': 'short_fee_rate',
                           'longInitialMargin': 'long_initial_margin', 'contractMonth': 'contract_month',
                           'longMaintenanceMargin': 'long_maintenance_margin', 'primaryExchange': 'primary_exchange',
                           'tradingClass': 'trading_class', 'lastTradingDate': 'last_trading_date',
                           'minTick': 'min_tick', 'firstNoticeDate': 'first_notice_date',
                           'lastBiddingCloseTime': 'last_bidding_close_time'}


class ContractsResponse(TigerResponse):
    def __init__(self):
        super(ContractsResponse, self).__init__()
        self.contracts = []
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(ContractsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = self.data if isinstance(self.data, dict) else json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    contract_fields = {}
                    for key, value in item.items():
                        if value is None:
                            continue
                        tag = CONTRACT_FIELD_MAPPINGS[key] if key in CONTRACT_FIELD_MAPPINGS else key
                        if tag in CONTRACT_FIELDS:
                            contract_fields[tag] = value

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
                    name = contract_fields.get('name')
                    short_margin = contract_fields.get('short_margin')
                    short_fee_rate = contract_fields.get('short_fee_rate')
                    shortable = contract_fields.get('shortable')
                    long_initial_margin = contract_fields.get('long_initial_margin')
                    long_maintenance_margin = contract_fields.get('long_maintenance_margin')
                    contract_month = contract_fields.get('contract_month')
                    identifier = contract_fields.get('identifier')
                    primary_exchange = contract_fields.get('primary_exchange')
                    market = contract_fields.get('market')
                    min_tick = contract_fields.get('min_tick')
                    trading_class = contract_fields.get('trading_class')
                    status = contract_fields.get('status')
                    continuous = contract_fields.get('continuous')
                    trade = contract_fields.get('trade')
                    last_trading_date = contract_fields.get('last_trading_date')
                    first_notice_date = contract_fields.get('first_notice_date')
                    last_bidding_close_time = contract_fields.get('last_bidding_close_time')
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type, exchange=exchange,
                                        origin_symbol=origin_symbol, local_symbol=local_symbol, expiry=expiry,
                                        strike=strike, put_call=put_call, multiplier=multiplier, name=name,
                                        short_margin=short_margin, short_fee_rate=short_fee_rate, shortable=shortable,
                                        long_initial_margin=long_initial_margin, contract_month=contract_month,
                                        long_maintenance_margin=long_maintenance_margin, identifier=identifier,
                                        primary_exchange=primary_exchange, market=market, min_tick=min_tick,
                                        trading_class=trading_class, status=status, continuous=continuous, trade=trade,
                                        last_trading_date=last_trading_date, first_notice_date=first_notice_date,
                                        last_bidding_close_time=last_bidding_close_time)
                    self.contracts.append(contract)
