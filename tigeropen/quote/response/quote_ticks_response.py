# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import json
from tigeropen.common.response import TigerResponse
from tigeropen.quote.domain.tick import TradeTick


class TradeTickResponse(TigerResponse):
    def __init__(self):
        super(TradeTickResponse, self).__init__()
        self.trade_ticks = []
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(TradeTickResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                index = data_json.get('beginIndex')
                for item in data_json['items']:
                    trade_tick = TradeTick()
                    
                    for key, value in item.items():
                        if value is None:
                            continue
                        if key == 'type':
                            trade_tick.direction = value
                        elif key == 'time':
                            trade_tick.timestamp = value
                        elif key == 'price':
                            trade_tick.price = value
                        elif key == 'volume':
                            trade_tick.size = value
                    if index is not None:
                        trade_tick.index = index
                        index += 1
                    self.trade_ticks.append(trade_tick)
