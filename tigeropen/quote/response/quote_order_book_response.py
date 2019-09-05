# -*- coding: utf-8 -*-
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string


class OrderBookResponse(TigerResponse):
    def __init__(self):
        super(OrderBookResponse, self).__init__()
        self.order_book = dict()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OrderBookResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            if len(self.data) == 1:
                for item in self.data:
                    symbol = get_string(item.get('symbol'))
                    asks = [(v['price'], v['volume'], v['count']) for v in item.get('asks', [])]
                    bids = [(v['price'], v['volume'], v['count']) for v in item.get('bids', [])]
                    self.order_book = {'symbol': symbol, 'asks': asks, 'bids': bids}
            else:
                for item in self.data:
                    symbol = get_string(item.get('symbol'))
                    asks = [(v['price'], v['volume'], v['count']) for v in item.get('asks', [])]
                    bids = [(v['price'], v['volume'], v['count']) for v in item.get('bids', [])]
                    self.order_book[symbol] = {'symbol': symbol, 'asks': asks, 'bids': bids}
            return self.order_book


