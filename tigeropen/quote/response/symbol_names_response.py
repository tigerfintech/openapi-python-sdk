# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import json
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string


class SymbolNamesResponse(TigerResponse):
    def __init__(self):
        super(SymbolNamesResponse, self).__init__()
        self.symbol_names = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SymbolNamesResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                self.symbol_names = [(get_string(item['symbol']), get_string(item['name'])) for item in
                                     data_json['items'] if len(item) == 2]
