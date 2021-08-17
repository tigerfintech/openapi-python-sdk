# -*- coding: utf-8 -*-

import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'field', 'date', 'value']


class FinancialDailyResponse(TigerResponse):
    def __init__(self):
        super(FinancialDailyResponse, self).__init__()
        self.financial_daily = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FinancialDailyResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            items = list()
            for item in self.data:
                item_values = dict()
                for key, value in item.items():
                    item_values[key] = value
                items.append(item_values)
            self.financial_daily = pd.DataFrame(items, columns=COLUMNS)
