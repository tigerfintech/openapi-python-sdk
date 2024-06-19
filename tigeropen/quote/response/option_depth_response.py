# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse


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
                item = self.data[0]
                symbol = item.get('symbol')
                asks = [(v['price'], v['volume'], v['count']) for v in item.get('asks', [])]
                bids = [(v['price'], v['volume'], v['count']) for v in item.get('bids', [])]
                self.result = {'symbol': symbol, 'asks': asks, 'bids': bids}
            else:
                for item in self.data:
                    symbol = item.get('symbol')
                    asks = [(v['price'], v['volume'], v['count']) for v in item.get('asks', [])]
                    bids = [(v['price'], v['volume'], v['count']) for v in item.get('bids', [])]
                    self.result[symbol] = {'symbol': symbol, 'asks': asks, 'bids': bids}
            return self.result


