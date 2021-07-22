# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'time', 'price', 'avg_price', 'pre_close', 'volume', 'trading_session']
TIMELINE_FIELD_MAPPINGS = {'avgPrice': 'avg_price'}


class QuoteTimelineResponse(TigerResponse):
    def __init__(self):
        super(QuoteTimelineResponse, self).__init__()
        self.timelines = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteTimelineResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            timeline_items = []
            for symbol_item in self.data:
                symbol = symbol_item.get('symbol')
                pre_close = symbol_item.get('preClose')
                if 'preMarket' in symbol_item:  # 盘前
                    pre_markets = symbol_item['preMarket'].get('items')
                    if pre_markets:
                        for item in pre_markets:
                            item_values = self.parse_timeline(item, symbol, pre_close, 'pre_market')
                            timeline_items.append([item_values.get(tag) for tag in COLUMNS])

                if 'intraday' in symbol_item:  # 盘中
                    regulars = symbol_item['intraday'].get('items')
                elif 'items' in symbol_item:
                    regulars = symbol_item['items'][0].get('items')
                else:
                    regulars = None
                if regulars:
                    for item in regulars:
                        item_values = self.parse_timeline(item, symbol, pre_close, 'regular')
                        timeline_items.append([item_values.get(tag) for tag in COLUMNS])

                if 'afterHours' in symbol_item:  # 盘后
                    after_hours = symbol_item['afterHours'].get('items')
                    if after_hours:
                        for item in after_hours:
                            item_values = self.parse_timeline(item, symbol, pre_close, 'after_hours')
                            timeline_items.append([item_values.get(tag) for tag in COLUMNS])

            self.timelines = pd.DataFrame(timeline_items, columns=COLUMNS)

    @staticmethod
    def parse_timeline(item, symbol, pre_close, trading_session):
        item_values = {'symbol': symbol, 'pre_close': pre_close, 'trading_session': trading_session}
        for key, value in item.items():
            if value is None:
                continue
            tag = TIMELINE_FIELD_MAPPINGS[key] if key in TIMELINE_FIELD_MAPPINGS else key
            item_values[tag] = value

        return item_values
