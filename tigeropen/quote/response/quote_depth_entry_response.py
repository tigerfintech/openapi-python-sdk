# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string


class DepthEntryResponse(TigerResponse):
    def __init__(self):
        super(DepthEntryResponse, self).__init__()
        self.depth_entry = dict()
        self._is_success = None

    def parse_response_content(self, response_content):
        """
        :return:
        { '02833': { 'asks': [
                        { 'count': 1, 'price': 27, 'volume': 3100 },
                        { 'count': 0, 'price': 27.05, 'volume': 0 },
                        .
                        .
                        { 'count': 1, 'price': 27.45, 'volume': 300 }],
                    'bids': [
                        { 'count': 1, 'price': 26.85, 'volume': 1000 },
                        { 'count': 0, 'price': 26.8, 'volume': 0 },
                        .
                        .
                        { 'count': 0, 'price': 26.4, 'volume': 0 } ],
                    'symbol': '02833' },
        '02828': { 'asks': [
                        { 'count': 3, 'price': 103.3, 'volume': 172200 },
                        .
                        .
                        { 'count': 2, 'price': 104.2, 'volume': 5200 } ],
                    'bids': [
                        { 'count': 3, 'price': 103.2, 'volume': 166200 },
                        .
                        .
                        { 'count': 1, 'price': 102.3, 'volume': 88800 } ],
                    'symbol': '02828' }
        }
        """
        response = super(DepthEntryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            for item in self.data:
                symbol = get_string(item.get('symbol'))
                self.depth_entry[symbol] = item
            return self.depth_entry


