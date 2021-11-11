# -*- coding: utf-8 -*-
"""
Created on 2021/11/11

@author: sukai
"""

import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'ask_price', 'ask_size', 'bid_price', 'bid_size', 'pre_close', 'latest_price', 'latest_time',
           'volume', 'open', 'high', 'low', 'status']
BRIEF_FIELD_MAPPINGS = {'askPrice': 'ask_price', 'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                        'latestPrice': 'latest_price', 'preClose': 'pre_close', 'latestTime': 'latest_time',
                        'avgPrice': 'avg_price', 'adjPreClose': 'adj_pre_close'}


class DelayBriefsResponse(TigerResponse):
    def __init__(self):
        super(DelayBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(DelayBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            self.briefs = pd.DataFrame(self.data).rename(columns=BRIEF_FIELD_MAPPINGS)
