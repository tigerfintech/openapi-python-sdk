# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline, camel_to_underline_obj
from tigeropen.trade.domain.contract import Contract

CONTRACT_FIELD_MAPPINGS = {'conid': 'contract_id', 'right': 'put_call', 'tradeable': 'trade'}


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
            if 'items' in self.data:
                items = self.data['items']
            elif isinstance(self.data, list):
                items = self.data
            else:
                items = [self.data]
            for item in items:
                contract_fields = {}
                for key, value in item.items():
                    tag = CONTRACT_FIELD_MAPPINGS[key] if key in CONTRACT_FIELD_MAPPINGS else camel_to_underline(key)
                    if isinstance(value, (list, dict)):
                        value = camel_to_underline_obj(value)
                    contract_fields[tag] = value
                contract = Contract()
                for k, v in contract_fields.items():
                    setattr(contract, k, v)
                self.contracts.append(contract)
