# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline
FIELD_MAP = {
    'dates': 'date',
    'timestamps': 'timestamp',
    'periodTags': 'period_tag',
    'optionSymbols': 'option_symbol'
}

class OptionExpirationsResponse(TigerResponse):
    def __init__(self):
        super(OptionExpirationsResponse, self).__init__()
        self.expirations = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionExpirationsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            for item in self.data:
                item.pop('count', None)
                self.expirations = pd.concat([self.expirations, pd.DataFrame(item)])
            column_map = {col: FIELD_MAP.get(col, camel_to_underline(col)) for col in self.expirations.columns.to_list()}
            self.expirations.rename(columns=column_map, inplace=True)
            self.expirations.reset_index(inplace=True, drop=True)
