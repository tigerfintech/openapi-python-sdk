# -*- coding: utf-8 -*-

import pandas as pd

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj


class QuoteOvernightResponse(TigerResponse):
    def __init__(self):
        super(QuoteOvernightResponse, self).__init__()
        self.result = None
        
    def parse_response_content(self, response_content):
        response = super(QuoteOvernightResponse, self).parse_response_content(response_content)
        if 'data' in response:
            data = camel_to_underline_obj(response['data'])
            self.result = pd.DataFrame(data)
        return response 