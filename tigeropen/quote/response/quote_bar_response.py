# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume', 'next_page_token']
BAR_FIELD_MAPPINGS = {'avgPrice': 'avg_price'}


class QuoteBarResponse(TigerResponse):
    def __init__(self):
        super(QuoteBarResponse, self).__init__()
        self.bars = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteBarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            bar_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                next_page_token = symbol_item.get('nextPageToken')
                if 'items' in symbol_item:
                    for item in symbol_item['items']:
                        item_values = {'symbol': symbol, 'next_page_token': next_page_token}
                        for key, value in item.items():
                            if value is None:
                                continue
                            tag = BAR_FIELD_MAPPINGS[key] if key in BAR_FIELD_MAPPINGS else key
                            item_values[tag] = value
                        bar_items.append([item_values.get(tag) for tag in COLUMNS])

            self.bars = pd.DataFrame(bar_items, columns=COLUMNS)
