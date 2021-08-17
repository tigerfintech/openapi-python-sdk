# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['symbol', 'lot_size', 'min_tick', 'spread_scale']
BRIEF_FIELD_MAPPINGS = {'lotSize': 'lot_size', 'minTick': 'min_tick', 'spreadScale': 'spread_scale'}


class TradeMetaResponse(TigerResponse):
    def __init__(self):
        super(TradeMetaResponse, self).__init__()
        self.metas = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(TradeMetaResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            meta_data = []
            for item in self.data:
                item_values = {}
                for key, value in item.items():
                    if value is None:
                        continue
                    tag = BRIEF_FIELD_MAPPINGS[key] if key in BRIEF_FIELD_MAPPINGS else key
                    item_values[tag] = value

                meta_data.append([item_values.get(tag) for tag in COLUMNS])

            self.metas = pd.DataFrame(meta_data, columns=COLUMNS)
