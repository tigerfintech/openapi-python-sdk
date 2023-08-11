# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

from tigeropen.common.response import TigerResponse


class SymbolsResponse(TigerResponse):
    def __init__(self):
        super(SymbolsResponse, self).__init__()
        self.result = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SymbolsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            self.result = [symbol for symbol in self.data if symbol]
