# -*- coding: utf-8 -*-
#
# @Date    : 2022/4/13
# @Author  : sukai

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline



class FundContractsResponse(TigerResponse):
    def __init__(self):
        super(FundContractsResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FundContractsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            fields = self.data[0].keys()
            fields_map = {origin: camel_to_underline(origin) for origin in fields}
            df = pd.DataFrame(self.data)
            self.result = df.rename(columns=fields_map)
