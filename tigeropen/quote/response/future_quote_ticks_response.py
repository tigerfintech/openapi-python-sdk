# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['identifier', 'index', 'time', 'price', 'volume']


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
            for symbol_item in self.data:
                identifier = symbol_item.get('contractCode')
                if 'items' in symbol_item:
                    for item in symbol_item['items'][::-1]:
                        item_values = {'identifier': identifier}
                        for key, value in item.items():
                            if value is None:
                                continue
                            item_values[key] = value
                        tick_items.append([item_values.get(tag) for tag in COLUMNS])

            self.trade_ticks = pd.DataFrame(tick_items, columns=COLUMNS)
