# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse


class FutureDepthResponse(TigerResponse):
    def __init__(self):
        super(FutureDepthResponse, self).__init__()
        self.result = dict()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureDepthResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            if len(self.data) == 1:
                item = self.data[0]
                identifier = item.get('contractCode')
                asks = [(v.get('price'), v.get('volume')) for v in item.get('ask', [])]
                bids = [(v.get('price'), v.get('volume')) for v in item.get('bid', [])]
                self.result = {'identifier': identifier, 'asks': asks, 'bids': bids}
            else:
                for item in self.data:
                    identifier = item.get('contractCode')
                    asks = [(v.get('price'), v.get('volume')) for v in item.get('ask', [])]
                    bids = [(v.get('price'), v.get('volume')) for v in item.get('bid', [])]
                    self.result[identifier] = {'identifier': identifier, 'asks': asks, 'bids': bids}
            return self.result


