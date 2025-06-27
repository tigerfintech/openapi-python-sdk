# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.contract_utils import get_option_identifier


class OptionDepthQuoteResponse(TigerResponse):
    def __init__(self):
        super(OptionDepthQuoteResponse, self).__init__()
        self.result = dict()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionDepthQuoteResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            if len(self.data) == 1:
                self.result = self.parse_data(self.data[0])
            else:
                for item in self.data:
                    info = self.parse_data(item)
                    identifier = info.get('identifier')
                    self.result[identifier] = info
            return self.result

    def parse_data(self, item):
        symbol = item.get('symbol', '')
        expiry = item.get('expiry', '')
        strike = item.get('strike', '')
        right = item.get('right', '')
        identifier = get_option_identifier(symbol, expiry, right, strike)
        asks = [(v['price'], v.get('volume', 0), v.get('timestamp', 0), v.get('code')) for v in item.get('ask', [])]
        bids = [(v['price'], v.get('volume', 0), v.get('timestamp', 0), v.get('code')) for v in item.get('bid', [])]
        return {'identifier': identifier, 'asks': asks, 'bids': bids}


