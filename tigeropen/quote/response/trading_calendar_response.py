# -*- coding: utf-8 -*-
# 
# @Date    : 2021-04-16
# @Author  : sukai
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils


class TradingCalendarResponse(TigerResponse):
    def __init__(self):
        super(TradingCalendarResponse, self).__init__()
        self.calendar = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TradingCalendarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.calendar = string_utils.camel_to_underline_obj(self.data)
