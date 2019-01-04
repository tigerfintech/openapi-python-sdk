# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six
import pandas as pd

from tigeropen.common.util.string_utils import get_string
from tigeropen.common.response import TigerResponse

COLUMNS = ['time', 'latest_time', 'open', 'high', 'low', 'close', 'settlement', 'volume', 'open_interest']
BAR_FIELD_MAPPINGS = {'avgPrice': 'avg_price', 'openInterest': 'open_interest', 'lastTime': 'latest_time'}


class FutureQuoteBarResponse(TigerResponse):
    def __init__(self):
        super(FutureQuoteBarResponse, self).__init__()
        self.bars = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureQuoteBarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            bar_items = []
            for item in self.data:
                item_values = dict()
                for key, value in item.items():
                    if value is None:
                        continue
                    if isinstance(value, six.string_types):
                        value = get_string(value)
                    # if 'time' == key or 'lastTime' == key:
                    #     value = pd.Timestamp(value, unit='ms', tzinfo=eastern)
                    tag = BAR_FIELD_MAPPINGS[key] if key in BAR_FIELD_MAPPINGS else key
                    item_values[tag] = value
                bar_items.append([item_values.get(tag) for tag in COLUMNS])

            self.bars = pd.DataFrame(bar_items, columns=COLUMNS)
