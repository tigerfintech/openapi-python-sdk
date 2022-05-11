# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['identifier', 'time', 'latest_time', 'open', 'high', 'low', 'close', 'settlement', 'volume',
           'open_interest', 'next_page_token']
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
            for symbol_item in self.data:
                identifier = symbol_item.get('contractCode')
                next_page_token = symbol_item.get('nextPageToken')
                if 'items' in symbol_item:
                    for item in symbol_item['items']:
                        item_values = {'identifier': identifier, 'next_page_token': next_page_token}
                        for key, value in item.items():
                            if value is None:
                                continue
                            tag = BAR_FIELD_MAPPINGS[key] if key in BAR_FIELD_MAPPINGS else key
                            item_values[tag] = value
                        bar_items.append([item_values.get(tag) for tag in COLUMNS])

            self.bars = pd.DataFrame(bar_items, columns=COLUMNS)
