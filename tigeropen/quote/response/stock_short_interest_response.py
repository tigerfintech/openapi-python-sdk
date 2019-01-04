# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six

import pandas as pd
from tigeropen.common.util.string_utils import get_string
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'settlement_date', 'short_interest', 'avg_daily_volume', 'days_to_cover', 'percent_of_float']
SHORT_INTEREST_FIELD_MAPPINGS = {'settlementDate': 'settlement_date', 'shortInterest': 'short_interest',
                                 'avgDailyVolume': 'avg_daily_volume', 'daysToCover': 'days_to_cover',
                                 'percentOfFloat': 'percent_of_float'}


class ShortInterestResponse(TigerResponse):
    def __init__(self):
        super(ShortInterestResponse, self).__init__()
        self.short_interests = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(ShortInterestResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            short_interest_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                items = symbol_item.get('items')
                for item in items:
                    item_values = {'symbol': symbol}
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
                        tag = SHORT_INTEREST_FIELD_MAPPINGS[key] if key in SHORT_INTEREST_FIELD_MAPPINGS else key
                        item_values[tag] = value
                    short_interest_items.append([item_values.get(tag) for tag in COLUMNS])

            self.short_interests = pd.DataFrame(short_interest_items, columns=COLUMNS)
