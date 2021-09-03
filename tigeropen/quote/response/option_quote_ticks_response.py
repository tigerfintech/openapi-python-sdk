# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.common_utils import eastern
from tigeropen.common.util.contract_utils import get_option_identifier

COLUMNS = ['identifier', 'symbol', 'expiry', 'put_call', 'strike', 'time', 'price', 'volume']


class OptionTradeTickResponse(TigerResponse):
    def __init__(self):
        super(OptionTradeTickResponse, self).__init__()
        self.trade_ticks = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionTradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            tick_items = []
            for symbol_item in self.data:
                if 'items' in symbol_item and len(symbol_item['items']) > 0:
                    underlying_symbol = symbol_item.get('symbol')
                    put_call = symbol_item.get('right').upper()
                    expiry = symbol_item.get('expiry')
                    strike = float(symbol_item.get('strike'))
                    identifier = symbol_item.get('identifier')
                    if not identifier:
                        expiration = pd.Timestamp(expiry, unit='ms', tzinfo=eastern).date().strftime("%Y%m%d")
                        identifier = get_option_identifier(underlying_symbol, expiration, put_call, strike)

                    for item in symbol_item['items']:
                        item_values = {'identifier': identifier, 'symbol': underlying_symbol, 'expiry': expiry,
                                       'put_call': put_call, 'strike': strike}
                        for key, value in item.items():
                            if value is None:
                                continue
                            item_values[key] = value
                        tick_items.append([item_values.get(tag) for tag in COLUMNS])

            self.trade_ticks = pd.DataFrame(tick_items, columns=COLUMNS)
