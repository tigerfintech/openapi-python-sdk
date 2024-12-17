# -*- coding: utf-8 -*-
#
# @Date    : 2022/4/13
# @Author  : sukai

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils


class QuoteDataframeResponse(TigerResponse):
    def __init__(self):
        super(QuoteDataframeResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteDataframeResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        data_items = []
        if self.data and isinstance(self.data, list):
            for symbol_item in self.data:
                df = pd.DataFrame(symbol_item.get('items'))
                df.insert(0, 'symbol', symbol_item.get('symbol'))
                data_items.append(df)
            final_df = pd.concat(data_items)
        elif isinstance(self.data, dict) and 'items' in self.data:
            final_df = pd.DataFrame(self.data['items'])
        else:
            return
        field_mapping = {item: string_utils.camel_to_underline(item) for item in final_df.columns}
        self.result = final_df.rename(columns=field_mapping)
