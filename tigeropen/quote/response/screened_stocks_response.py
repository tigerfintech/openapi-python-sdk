# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/18
# @Author  : sukai
from tigeropen.common.response import TigerResponse


class ScreenedStocksResponse(TigerResponse):
    def __init__(self):
        super(ScreenedStocksResponse, self).__init__()
        self.stocks = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(ScreenedStocksResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data and isinstance(self.data, list):
            stocks = []