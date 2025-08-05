# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline

BRIEF_FIELD_MAPPINGS = {'right': 'put_call', 'contractCode': 'identifier'}


class FutureBriefsResponse(TigerResponse):
    def __init__(self):
        super(FutureBriefsResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            if isinstance(self.data, list):
                fields_map = {origin: camel_to_underline(origin) for origin in self.data[0].keys()}
                df = pd.DataFrame(self.data)
            else:
                fields_map = {origin: camel_to_underline(origin) for origin in self.data.keys()}
                df = pd.DataFrame([self.data])
            fields_map.update(BRIEF_FIELD_MAPPINGS)
            self.result = df.rename(columns=fields_map)
        else:
            self.result = pd.DataFrame()