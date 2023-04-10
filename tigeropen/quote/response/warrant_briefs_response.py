# -*- coding: utf-8 -*-
# 
# @Date    : 2023/4/6
# @Author  : sukai
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils


class WarrantBriefsResponse(TigerResponse):
    def __init__(self):
        super(WarrantBriefsResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(WarrantBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and self.data.get('items'):
            self.result = string_utils.camel_to_underline_obj(self.data.get('items'))
            self.result = pd.DataFrame(self.result)
