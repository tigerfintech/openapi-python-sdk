# -*- coding: utf-8 -*-
# 
# @Date    : 2023/4/7
# @Author  : sukai
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.quote.domain.filter import WarrantFilterItem, WarrantFilterBounds


class WarrantFilterResponse(TigerResponse):
    def __init__(self):
        super(WarrantFilterResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(WarrantFilterResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data = string_utils.camel_to_underline_obj(self.data)
            items = pd.DataFrame(data.pop('items'))
            bounds = WarrantFilterBounds(**data.pop('bounds'))
            self.result = WarrantFilterItem(**data, items=items, bounds=bounds)
