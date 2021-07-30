# -*- coding: utf-8 -*-

import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'currency', 'field', 'value', 'period_end_date', 'filing_date']
REPORT_FIELD_MAPPINGS = {'periodEndDate': 'period_end_date', 'filingDate': 'filing_date'}


class FinancialReportResponse(TigerResponse):
    def __init__(self):
        super(FinancialReportResponse, self).__init__()
        self.financial_report = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FinancialReportResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            items = list()
            for item in self.data:
                item_values = dict()
                for key, value in item.items():
                    item_values[key] = value
                items.append(item_values)
            self.financial_report = pd.DataFrame(items).rename(columns=REPORT_FIELD_MAPPINGS)[COLUMNS]
