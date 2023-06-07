# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'index', 'time', 'price', 'volume', 'direction']


class TradeTickResponse(TigerResponse):
    def __init__(self):
        super(TradeTickResponse, self).__init__()
        self.trade_ticks = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        # v2: {'data': [{'symbol': 'AAPL', 'beginIndex': 724203, 'endIndex': 724403,
        # 'items': [{'time': 1663963199040, 'volume': 200, 'price': 150.66, 'type': '+'},
        # {'time': 1663963199051, 'volume': 100, 'price': 150.65, 'type': '-'},
        # {'time': 1663963199051, 'volume': 300, 'price': 150.65, 'type': '-'}]

        # v1: {'data': '{"beginIndex":722500,"endIndex":724403,
        # "items":[{"time":1663963192126,"volume":400,"price":150.5901,"type":"-"},
        # {"time":1663963192142,"volume":100,"price":150.61,"type":"+"}

        if self.data:
            # v2
            if isinstance(self.data, list):
                symbol_items = self.data
            else:
                symbol_items = [self.data]

            tick_items = []
            for symbol_item in symbol_items:
                symbol = symbol_item.get('symbol')
                if 'items' in symbol_item:
                    index = symbol_item.get('beginIndex')

                    for item in symbol_item['items']:
                        item_values = dict()
                        if symbol is not None:
                            item_values['symbol'] = symbol

                        for key, value in item.items():
                            if value is None:
                                continue

                            if key == 'type':
                                item_values['direction'] = value
                            else:
                                item_values[key] = value

                        if index is not None:
                            item_values['index'] = index
                            index += 1
                        tick_items.append(item_values)

            self.trade_ticks = pd.DataFrame(tick_items)
