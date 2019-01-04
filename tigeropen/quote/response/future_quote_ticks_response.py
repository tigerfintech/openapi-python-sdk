# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six
import pandas as pd

from tigeropen.common.util.string_utils import get_string
from tigeropen.common.response import TigerResponse

COLUMNS = ['index', 'time', 'price', 'volume']


class FutureTradeTickResponse(TigerResponse):
    def __init__(self):
        super(FutureTradeTickResponse, self).__init__()
        self.trade_ticks = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureTradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            tick_items = []
            for item in self.data[::-1]:
                item_values = dict()
                for key, value in item.items():
                    if value is None:
                        continue
                    if isinstance(value, six.string_types):
                        value = get_string(value)
                    item_values[key] = value
                tick_items.append([item_values.get(tag) for tag in COLUMNS])

            self.trade_ticks = pd.DataFrame(tick_items, columns=COLUMNS)
