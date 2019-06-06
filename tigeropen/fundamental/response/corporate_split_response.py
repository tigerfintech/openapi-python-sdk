# -*- coding: utf-8 -*-

import pandas as pd
from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'action_type', 'from_factor', 'to_factor', 'ratio', 'execute_date', 'market', 'exchange']
SPLIT_FIELD_MAPPINGS = {'actionType': 'action_type', 'fromFactor': 'from_factor', 'toFactor': 'to_factor',
                        'executeDate': 'execute_date'}


class CorporateSplitResponse(TigerResponse):
    def __init__(self):
        super(CorporateSplitResponse, self).__init__()
        self.corporate_split = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(CorporateSplitResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            items = list()
            for symbol, split_items in self.data.items():
                for item in split_items:
                    item['symbol'] = symbol
                    items.append(item)
            self.corporate_split = pd.DataFrame(items).rename(columns=SPLIT_FIELD_MAPPINGS)[COLUMNS]
