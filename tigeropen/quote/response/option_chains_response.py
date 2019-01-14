# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six
import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string

COLUMNS = ['identifier', 'symbol', 'expiry', 'strike', 'put_call', 'multiplier', 'ask_price', 'ask_size', 'bid_price',
           'bid_size', 'pre_close', 'latest_price', 'volume', 'open_interest']
CHAIN_FIELD_MAPPINGS = {'askPrice': 'ask_price', 'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                        'latestPrice': 'latest_price', 'openInterest': 'open_interest', 'preClose': 'pre_close',
                        'right': 'put_call'}


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
                                if isinstance(value, six.string_types):
                                    value = get_string(value)
                                if key == 'right':
                                    value = value.upper()
                                tag = CHAIN_FIELD_MAPPINGS[key] if key in CHAIN_FIELD_MAPPINGS else key
                                item_values[tag] = value
                            chain_data.append([item_values.get(tag) for tag in COLUMNS])

            self.chain = pd.DataFrame(chain_data, columns=COLUMNS)
