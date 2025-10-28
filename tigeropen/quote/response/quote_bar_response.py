# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline


class QuoteBarResponse(TigerResponse):
    def __init__(self):
        super(QuoteBarResponse, self).__init__()
        self.result = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content):
        super(QuoteBarResponse, self).parse_response_content(response_content)

        if self.data and isinstance(self.data, list):
            bar_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                next_page_token = symbol_item.get('nextPageToken')
                if 'items' in symbol_item:
                    for item in symbol_item['items']:
                        item_values = {'symbol': symbol, 'next_page_token': next_page_token}
                        item_values.update(item)
                        bar_items.append(item_values)

            self.result = pd.DataFrame(bar_items)
            column_map = {col: camel_to_underline(col) for col in self.result.columns.to_list()}
            self.result.rename(columns=column_map, inplace=True)
            self.result.reset_index(inplace=True, drop=True)
