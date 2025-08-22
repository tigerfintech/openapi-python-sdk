# -*- coding: utf-8 -*-

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline, camel_to_underline_obj


class FundDetailsResponse(TigerResponse):
    def __init__(self):
        super(FundDetailsResponse, self).__init__()
        self.result = pd.DataFrame()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FundDetailsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data = {camel_to_underline(k): v for k, v in self.data.items()}
            items = data.get('items')
            if items:
                self.result = pd.DataFrame([camel_to_underline_obj(i) for i in items])
                self.result['page'] = data['page']
                self.result['limit'] = data['limit']
                self.result['item_count'] = data['item_count']
                self.result['page_count'] = data['page_count']
                self.result['timestamp'] = data['timestamp']