# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd
from tigeropen.common.response import TigerResponse


class OptionExpirationsResponse(TigerResponse):
    def __init__(self):
        super(OptionExpirationsResponse, self).__init__()
        self.expirations = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionExpirationsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            expiration_items = []
            for item in self.data:
                symbol = item.get('symbol')
                dates = item.get('dates')
                timestamps = item.get('timestamps')

                if symbol and dates:
                    for date, timestamp in zip(dates, timestamps):
                        expiration_items.append([symbol, date, timestamp])

            self.expirations = pd.DataFrame(expiration_items, columns=['symbol', 'date', 'timestamp'])
