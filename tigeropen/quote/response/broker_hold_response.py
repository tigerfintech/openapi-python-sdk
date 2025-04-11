import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils

class BrokerHoldResponse(TigerResponse):
    def __init__(self):
        super().__init__()
        self.result = None
        self._is_success = None
        
    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            formated_data = string_utils.camel_to_underline_obj(self.data)
            items = formated_data.get('items')
            result = pd.DataFrame(data=items)
            result['page'] = formated_data.get('page')
            result['total_page'] = formated_data.get('total_page')
            result['total_count'] = formated_data.get('total_count')
            self.result = result

