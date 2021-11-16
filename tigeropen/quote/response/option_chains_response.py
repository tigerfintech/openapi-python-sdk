# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils

CHAIN_FIELD_MAPPINGS = {'right': 'put_call'}


class OptionChainsResponse(TigerResponse):
    def __init__(self):
        super(OptionChainsResponse, self).__init__()
        self.chain = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionChainsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data and isinstance(self.data, list):
            chain_data = []
            for item in self.data:
                symbol = item.get('symbol')
                expiry = item.get('expiry')
                items = item.get('items')
                if symbol and items:
                    for chain_item in items:
                        for call_put_item in chain_item.values():
                            item_values = {'symbol': symbol, 'expiry': expiry}
                            for key, value in call_put_item.items():
                                if value is None:
                                    continue
                                if key == 'right':
                                    value = value.upper()
                                item_values[CHAIN_FIELD_MAPPINGS.get(key, string_utils.camel_to_underline(key))] = value
                            chain_data.append(item_values)
            self.chain = pd.DataFrame(chain_data)
