# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import json
import pytz
import dateutil.parser as dateparser

from tigeropen.common.util.string_utils import get_string
from tigeropen.quote.domain.market_status import MarketStatus
from tigeropen.common.response import TigerResponse

eastern = pytz.timezone('US/Eastern')
china = pytz.timezone('Asia/Shanghai')
hongkong = pytz.timezone('Asia/Hong_Kong')


class MarketStatusResponse(TigerResponse):
    def __init__(self):
        super(MarketStatusResponse, self).__init__()
        self.markets = []
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(MarketStatusResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    market, status, open_time = None, None, None
                    for key, value in item.items():
                        if value is None:
                            continue
                        if key == 'market':
                            market = get_string(value)
                        elif key == 'marketStatus':
                            status = get_string(value)
                        elif key == 'openTime':
                            if value.endswith(' EDT') or value.endswith(' EST'):
                                value = value[0:len(value) - 4]
                            open_time = dateparser.parse(value)
                    if open_time and market:
                        if market == 'US':
                            open_time = eastern.localize(open_time)
                        elif market == 'HK':
                            open_time = hongkong.localize(open_time)
                        elif market == 'CN':
                            open_time = china.localize(open_time)
                    market_status = MarketStatus(market, status, open_time)
                    self.markets.append(market_status)
