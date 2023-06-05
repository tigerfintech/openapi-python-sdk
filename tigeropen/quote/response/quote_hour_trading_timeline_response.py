# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json

import pandas as pd

from tigeropen.common.consts import TradingSession
from tigeropen.common.response import TigerResponse
from tigeropen.quote.domain.quote_brief import HourTrading

COLUMNS = ['time', 'price', 'avg_price', 'pre_close', 'volume']
TIMELINE_FIELD_MAPPINGS = {'avgPrice': 'avg_price'}
BRIEF_FIELD_MAPPINGS = {'open': 'open_price', 'high': 'high_price', 'low': 'low_price', 'preClose': 'prev_close',
                        'latestPrice': 'latest_price'}


class QuoteHourTradingTimelineResponse(TigerResponse):
    def __init__(self):
        super(QuoteHourTradingTimelineResponse, self).__init__()
        self.timelines = []
        self.hour_trading = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteHourTradingTimelineResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = self.data
            pre_close = data_json.get('preClose')
            if 'detail' in data_json:
                detail = data_json['detail']
                hour_trading = HourTrading()
                if 'timestamp' in response:
                    hour_trading.latest_time = response['timestamp']

                for key, value in detail.items():
                    if value is None:
                        continue
                    if key == 'tag':
                        if value == '盘前':
                            hour_trading.trading_session = TradingSession.PreMarket
                        elif value == '盘后':
                            hour_trading.trading_session = TradingSession.AfterHours
                    else:
                        tag = BRIEF_FIELD_MAPPINGS[key] if key in BRIEF_FIELD_MAPPINGS else key
                        if hasattr(hour_trading, tag):
                            setattr(hour_trading, tag, value)
                self.hour_trading = hour_trading
            if 'items' in data_json:
                timeline_items = []
                for item in data_json['items']:
                    item_values = {'pre_close': pre_close}
                    for key, value in item.items():
                        if value is None:
                            continue
                        tag = TIMELINE_FIELD_MAPPINGS[key] if key in TIMELINE_FIELD_MAPPINGS else key
                        item_values[tag] = value
                    timeline_items.append([item_values.get(tag) for tag in COLUMNS])

                self.timelines = pd.DataFrame(timeline_items, columns=COLUMNS)
