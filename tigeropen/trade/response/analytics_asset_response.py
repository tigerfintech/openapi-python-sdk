# -*- coding: utf-8 -*-
# 
# @Date    : 2022/7/8
# @Author  : sukai
from datetime import datetime

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj


class AnalyticsAssetResponse(TigerResponse):
    def __init__(self):
        super().__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            result = camel_to_underline_obj(self.data)
            history = result.get('history')
            if history:
                for item in history:
                    item['dt'] = datetime.fromtimestamp(item['date'] // 1000).strftime('%Y-%m-%d')
            result['history'] = history
            self.result = result
