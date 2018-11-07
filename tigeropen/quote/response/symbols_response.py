# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import json
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string


class SymbolsResponse(TigerResponse):
    def __init__(self):
        super(SymbolsResponse, self).__init__()
        self.symbols = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SymbolsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                self.symbols = [get_string(symbol) for symbol in data_json['items'] if symbol]
