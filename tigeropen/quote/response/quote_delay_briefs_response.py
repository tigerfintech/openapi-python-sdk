# -*- coding: utf-8 -*-
"""
Created on 2021/11/11

@author: sukai
"""

import pandas as pd

from tigeropen.common.response import TigerResponse

from tigeropen.common.util import string_utils


class DelayBriefsResponse(TigerResponse):
    def __init__(self):
        super(DelayBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(DelayBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data and isinstance(self.data, list):
            df = pd.DataFrame(self.data)
            field_mapping = {item: string_utils.camel_to_underline(item) for item in df.columns}
            self.briefs = df.rename(columns=field_mapping)
