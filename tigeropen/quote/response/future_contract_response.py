# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils

CONTRACT_FIELD_MAPPINGS = {'ibCode': 'symbol'}
MAIN_CONTRACT_CODE_SUFFIX = 'main'
CONTRACT_CODE_COLUMN = 'contract_code'


class FutureContractResponse(TigerResponse):
    def __init__(self):
        super(FutureContractResponse, self).__init__()
        self.contracts = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content, skip_main=True):
        response = super(FutureContractResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            if isinstance(self.data, list):
                self.contracts = pd.DataFrame(self.data)
            elif isinstance(self.data, dict):
                self.contracts = pd.DataFrame([self.data])

            column_map = dict()
            for key in self.contracts.columns:
                column_map[key] = CONTRACT_FIELD_MAPPINGS.get(key, string_utils.camel_to_underline(key))
        
            self.contracts = self.contracts.rename(columns=column_map)
            
            # 重新排列列，将 contract_code 作为第一列，其余列按字母排序
            remaining_columns = sorted([col for col in self.contracts.columns if col != CONTRACT_CODE_COLUMN])
            all_columns = [CONTRACT_CODE_COLUMN] + remaining_columns
            self.contracts = self.contracts.reindex(columns=all_columns)

