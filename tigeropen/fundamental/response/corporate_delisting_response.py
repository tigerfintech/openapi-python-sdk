# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'action_type', 'announced_date', 'reason', 'execute_date', 'market', 'exchange']
FIELD_MAPPINGS = {'actionType': 'action_type', 'announcedDate': 'announced_date',
                  'executeDate': 'execute_date'}


class CorporateDelistingResponse(TigerResponse):
    def __init__(self):
        super(CorporateDelistingResponse, self).__init__()
        self.corporate_delisting = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(CorporateDelistingResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            items = []
            for symbol, delisting_items in self.data.items():
                for item in delisting_items:
                    item['symbol'] = symbol
                    items.append(item)
            df = pd.DataFrame(items).rename(columns=FIELD_MAPPINGS)
            self.corporate_delisting = df[[c for c in COLUMNS if c in df.columns]]
