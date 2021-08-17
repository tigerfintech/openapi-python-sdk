# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

from tigeropen.common.response import TigerResponse


class SymbolNamesResponse(TigerResponse):
    def __init__(self):
        super(SymbolNamesResponse, self).__init__()
        self.symbol_names = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SymbolNamesResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            self.symbol_names = [(item['symbol'], item['name']) for item in self.data if
                                 len(item) == 2]
