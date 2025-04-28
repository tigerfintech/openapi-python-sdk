# -*- coding: utf-8 -*-
"""
Created on 2024/03/21
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline


class FundingHistoryResponse(TigerResponse):
    def __init__(self):
        super(FundingHistoryResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FundingHistoryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            if isinstance(self.data, list):
                # 将驼峰命名转换为下划线命名
                items = [{camel_to_underline(k): v for k, v in item.items()} for item in self.data]
                self.result = pd.DataFrame(items)
            else:
                # 单个记录的情况
                items = {camel_to_underline(k): v for k, v in self.data.items()}
                self.result = pd.DataFrame([items])