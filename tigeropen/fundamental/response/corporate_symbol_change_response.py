# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'action_type', 'old_symbol', 'new_symbol', 'execute_date', 'market', 'exchange']
FIELD_MAPPINGS = {'actionType': 'action_type', 'oldSymbol': 'old_symbol', 'newSymbol': 'new_symbol',
                  'executeDate': 'execute_date'}


class CorporateSymbolChangeResponse(TigerResponse):
    def __init__(self):
        super(CorporateSymbolChangeResponse, self).__init__()
        self.corporate_symbol_change = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(CorporateSymbolChangeResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            items = []
            for symbol, change_items in self.data.items():
                for item in change_items:
                    item['symbol'] = symbol
                    items.append(item)
            df = pd.DataFrame(items).rename(columns=FIELD_MAPPINGS)
            self.corporate_symbol_change = df[[c for c in COLUMNS if c in df.columns]]
