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

COLUMNS = ['identifier', 'symbol', 'expiry', 'strike', 'put_call', 'multiplier', 'ask_price', 'ask_size', 'bid_price',
           'bid_size', 'pre_close', 'latest_price', 'latest_time', 'volume', 'open_interest', 'open', 'high', 'low',
           'rates_bonds', 'volatility', 'change']
BRIEF_FIELD_MAPPINGS = {'askPrice': 'ask_price', 'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                        'latestPrice': 'latest_price', 'openInterest': 'open_interest', 'preClose': 'pre_close',
                        'right': 'put_call', 'latestTime': 'latest_time', 'openInt': 'open_interest',
                        'ratesBonds': 'rates_bonds'}


class OptionBriefsResponse(TigerResponse):
    def __init__(self):
        super(OptionBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            brief_data = []
            for item in self.data:
                item_values = {}
                for key, value in item.items():
                    if value is None:
                        continue
                    if key == 'right':
                        value = value.upper()
                    tag = BRIEF_FIELD_MAPPINGS[key] if key in BRIEF_FIELD_MAPPINGS else key
                    item_values[tag] = value
                if 'identifier' not in item_values:
                    underlying_symbol = item_values.get('symbol')
                    expiry = item_values.get('expiry')
                    strike = float(item_values.get('strike'))
                    put_call = item_values.get('right')
                    if is_hk_option_underlying_symbol(underlying_symbol):
                        tz = get_tz_by_market(Market.HK)
                    else:
                        tz = get_tz_by_market(Market.US)
                    expiry = pd.Timestamp(expiry, unit='ms', tzinfo=tz).date().strftime("%Y%m%d")
                    item_values['identifier'] = get_option_identifier(underlying_symbol, expiry, put_call, strike)

                brief_data.append([item_values.get(tag) for tag in COLUMNS])

            self.briefs = pd.DataFrame(brief_data, columns=COLUMNS)
