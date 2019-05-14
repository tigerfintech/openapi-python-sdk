# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import six
import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string

COLUMNS = ['symbol', 'index', 'time', 'price', 'volume', 'direction']


class TradeTickResponse(TigerResponse):
    def __init__(self):
        super(TradeTickResponse, self).__init__()
        self.trade_ticks = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            tick_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                if 'items' in symbol_item:
                    index = symbol_item.get('beginIndex')

                    for item in symbol_item['items']:
                        item_values = {'symbol': symbol}

                        for key, value in item.items():
                            if value is None:
                                continue
                            if isinstance(value, six.string_types):
                                value = get_string(value)

                            if key == 'type':
                                item_values['direction'] = value
                            else:
                                item_values[key] = value

                        if index is not None:
                            item_values['index'] = index
                            index += 1
                        tick_items.append([item_values.get(tag) for tag in COLUMNS])

                self.trade_ticks = pd.DataFrame(tick_items, columns=COLUMNS)
