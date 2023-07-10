# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils

HOUR_TRADING_KEY = "hour_trading"


class StockBriefsResponse(TigerResponse):
    def __init__(self):
        super(StockBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(StockBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            brief_data = []
            for item in self.data:
                item_data = string_utils.camel_to_underline_obj(item)
                hour_trading = item_data.pop(HOUR_TRADING_KEY, None)
                if hour_trading:
                    for k, v in hour_trading.items():
                        item_data[HOUR_TRADING_KEY + '_' + k] = v
                brief_data.append(item_data)
            self.briefs = pd.DataFrame(brief_data)
