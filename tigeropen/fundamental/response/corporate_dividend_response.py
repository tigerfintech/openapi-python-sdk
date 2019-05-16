# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'contract_id', 'action_type', 'amount', 'currency', 'announced_date', 'execute_date',
           'record_date', 'pay_date', 'market', 'exchange', 'id']
DIVIDEND_FIELD_MAPPINGS = {'actionType': 'action_type', 'announcedDate': 'announced_date',
                           'executeDate': 'execute_date', 'recordDate': 'record_date', 'payDate': 'pay_date',
                           'contractId': 'contract_id'}


class CorporateDividendResponse(TigerResponse):
    def __init__(self):
        super(CorporateDividendResponse, self).__init__()
        self.corporate_dividend = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(CorporateDividendResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            dividend_data = list()
            for symbol, split_items in self.data.items():
                for item in split_items:
                    item['symbol'] = symbol
                    dividend_data.append(item)
            self.corporate_dividend = pd.DataFrame(dividend_data).rename(columns=DIVIDEND_FIELD_MAPPINGS)[COLUMNS]
