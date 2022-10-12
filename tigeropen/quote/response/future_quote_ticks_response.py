# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse


class FutureTradeTickResponse(TigerResponse):
    def __init__(self):
        super(FutureTradeTickResponse, self).__init__()
        self.trade_ticks = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureTradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.trade_ticks = pd.DataFrame(self.data.get('items', []))
            self.trade_ticks.insert(0, column='identifier', value=self.data.get('contractCode'))
