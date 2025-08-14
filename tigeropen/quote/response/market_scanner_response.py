# -*- coding: utf-8 -*-
# 
# @Date    : 2021/11/18
# @Author  : sukai
import json

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj
from tigeropen.quote.domain.filter import ScannerResult


class MarketScannerResponse(TigerResponse):
    def __init__(self):
        super(MarketScannerResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(MarketScannerResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            data = camel_to_underline_obj(self.data)
            self.result = ScannerResult(page=data.get('page'),
                                        page_size=data.get('page_size'),
                                        total_page=data.get('total_page'),
                                        total_count=data.get('total_count'),
                                        cursor_id=data.get('cursor_id'),
                                        items=data.get('items'))
        return self.result


class MarketScannerTagsResponse(TigerResponse):
    def __init__(self):
        super(MarketScannerTagsResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(MarketScannerTagsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            if isinstance(self.data, str):
                self.data = json.loads(self.data)
            data = camel_to_underline_obj(self.data)
            self.result = data
        return self.result