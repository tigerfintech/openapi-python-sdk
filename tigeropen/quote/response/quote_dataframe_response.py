# -*- coding: utf-8 -*-
#
# @Date    : 2022/4/13
# @Author  : sukai

import pandas as pd

from tigeropen.common.response import TigerResponse

FIELD_MAPPINGS = {'avgPrice': 'avg_price'}


class QuoteDataframeResponse(TigerResponse):
    def __init__(self):
        super(QuoteDataframeResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteDataframeResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            data_items = []
            for symbol_item in self.data:
                df = pd.DataFrame(symbol_item.get('items'))
                df.insert(0, 'symbol', symbol_item.get('symbol'))
                data_items.append(df)
            self.result = pd.concat(data_items).rename(columns=FIELD_MAPPINGS)
