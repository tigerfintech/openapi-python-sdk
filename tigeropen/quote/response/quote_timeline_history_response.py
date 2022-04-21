# -*- coding: utf-8 -*-
#
# @Date    : 2022/4/13
# @Author  : sukai

import pandas as pd

from tigeropen.common.response import TigerResponse

TIMELINE_FIELD_MAPPINGS = {'avgPrice': 'avg_price'}


class QuoteTimelineHistoryResponse(TigerResponse):
    def __init__(self):
        super(QuoteTimelineHistoryResponse, self).__init__()
        self.timelines = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteTimelineHistoryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            timeline_items = []
            for symbol_item in self.data:
                timeline_df = pd.DataFrame(symbol_item.get('items'))
                timeline_df.insert(0, 'symbol', symbol_item.get('symbol'))
                timeline_items.append(timeline_df)
            self.timelines = pd.concat(timeline_items).rename(columns=TIMELINE_FIELD_MAPPINGS)
