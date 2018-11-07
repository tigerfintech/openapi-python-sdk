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
from tigeropen.trade.response import CONTRACT_FIELDS

CONTRACT_FIELD_MAPPINGS = {'secType': 'sec_type', 'localSymbol': 'local_symbol', 'originSymbol': 'origin_symbol',
                           'conid': 'contract_id'}


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
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    contract_fields = {}
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
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
                    right = contract_fields.get('right')
                    multiplier = contract_fields.get('multiplier')
                    contract = Contract(symbol, currency, contract_id=contract_id, sec_type=sec_type, exchange=exchange,
                                        origin_symbol=origin_symbol, local_symbol=local_symbol, expiry=expiry,
                                        strike=strike, right=right, multiplier=multiplier)
                    self.contracts.append(contract)
