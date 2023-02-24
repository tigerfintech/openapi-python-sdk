# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'action_type', 'amount', 'currency', 'announced_date', 'execute_date',
           'record_date', 'pay_date', 'market', 'exchange']
DIVIDEND_FIELD_MAPPINGS = {'actionType': 'action_type', 'announcedDate': 'announced_date',
                           'executeDate': 'execute_date', 'recordDate': 'record_date', 'payDate': 'pay_date',
                           }


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
            items = list()
            for symbol, dividend_items in self.data.items():
                for item in dividend_items:
                    item['symbol'] = symbol
                    item['announcedDate'] = item.get('announcedDate', None)
                    items.append(item)
            self.corporate_dividend = pd.DataFrame(items).rename(columns=DIVIDEND_FIELD_MAPPINGS)
