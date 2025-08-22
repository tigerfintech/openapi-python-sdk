# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.consts import Market
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.common_utils import get_tz_by_market
from tigeropen.common.util.contract_utils import get_option_identifier, is_hk_option_underlying_symbol

COLUMNS = ['identifier', 'symbol', 'expiry', 'put_call', 'strike', 'time', 'open', 'high', 'low', 'close', 'volume',
           'open_interest']
BAR_FIELD_MAPPINGS = {'avgPrice': 'avg_price', 'openInterest': 'open_interest', 'right': 'put_call'}


class OptionQuoteBarResponse(TigerResponse):
    def __init__(self):
        super(OptionQuoteBarResponse, self).__init__()
        self.bars = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionQuoteBarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            bar_items = []
            for symbol_item in self.data:
                identifier = symbol_item.get('identifier')
                underlying_symbol = symbol_item.get('symbol')
                expiry = symbol_item.get('expiry')
                strike = float(symbol_item.get('strike'))
                put_call = symbol_item.get('right')
                if put_call:
                    put_call = put_call.upper()

                if not identifier:
                    if is_hk_option_underlying_symbol(underlying_symbol):
                        tz = get_tz_by_market(Market.HK)
                    else:
                        tz = get_tz_by_market(Market.US)
                    expiration = pd.Timestamp(expiry, unit='ms', tzinfo=tz).date().strftime("%Y%m%d")
                    identifier = get_option_identifier(underlying_symbol, expiration, put_call, strike)

                if 'items' in symbol_item:
                    for item in symbol_item['items']:
                        item_values = {'identifier': identifier, 'symbol': underlying_symbol, 'expiry': expiry,
                                       'put_call': put_call, 'strike': strike}
                        for key, value in item.items():
                            if value is None:
                                continue
                            tag = BAR_FIELD_MAPPINGS[key] if key in BAR_FIELD_MAPPINGS else key
                            item_values[tag] = value
                        bar_items.append([item_values.get(tag) for tag in COLUMNS])

            self.bars = pd.DataFrame(bar_items, columns=COLUMNS)
