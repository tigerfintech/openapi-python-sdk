# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse


class FutureExchangeResponse(TigerResponse):
    def __init__(self):
        super(FutureExchangeResponse, self).__init__()
        self.exchanges = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureExchangeResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            items = []
            for item in self.data:
                code, name, zone = None, None, None
                for key, value in item.items():
                    if value is None:
                        continue
                    if key == 'code':
                        code = value
                    elif key == 'name':
                        name = value
                    elif key == 'zoneId':
                        zone = value
                items.append([code, name, zone])
            self.exchanges = pd.DataFrame(items, columns=['code', 'name', 'zone'])
