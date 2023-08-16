# -*- coding: utf-8 -*-
#
# @Date    : 2023/8/11
# @Author  : sukai

import pandas as pd

from tigeropen.common.response import TigerResponse


class FinancialExchangeRateResponse(TigerResponse):
    def __init__(self):
        super(FinancialExchangeRateResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FinancialExchangeRateResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']


        if self.data and isinstance(self.data, list):
            data_items = []
            for currency_item in self.data:
                df = pd.DataFrame(currency_item.get('dailyValueList'))
                df.insert(0, 'currency', currency_item.get('currency'))
                data_items.append(df)
            self.result = pd.concat(data_items).reset_index(drop=True)
