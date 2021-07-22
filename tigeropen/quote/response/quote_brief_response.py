# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""

import json

from tigeropen.common.consts import TradingSession
from tigeropen.common.response import TigerResponse
from tigeropen.quote.domain.quote_brief import QuoteBrief, HourTrading

BRIEF_FIELD_MAPPINGS = {'latestPrice': 'latest_price', 'preClose': 'prev_close', 'secType': 'sec_type',
                        'timestamp': 'latest_time', 'askPrice': 'ask_price', 'askSize': 'ask_size',
                        'bidPrice': 'bid_price', 'bidSize': 'bid_size'}


class QuoteBriefResponse(TigerResponse):
    def __init__(self):
        super(QuoteBriefResponse, self).__init__()
        self.briefs = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteBriefResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    brief = QuoteBrief()
                    for key, value in item.items():
                        if value is None:
                            continue
                        if key == 'hourTrading':
                            hour_trading = HourTrading()
                            for sub_key, sub_value in value.items():
                                if sub_key == 'tag':
                                    if sub_value == '盘前':
                                        hour_trading.trading_session = TradingSession.PreMarket
                                    elif sub_value == '盘后':
                                        hour_trading.trading_session = TradingSession.AfterHours
                                else:
                                    sub_tag = BRIEF_FIELD_MAPPINGS[
                                        sub_key] if sub_key in BRIEF_FIELD_MAPPINGS else sub_key
                                    if hasattr(hour_trading, sub_tag):
                                        setattr(hour_trading, sub_tag, sub_value)
                            brief.hour_trading = hour_trading
                        else:
                            tag = BRIEF_FIELD_MAPPINGS[key] if key in BRIEF_FIELD_MAPPINGS else key
                            if hasattr(brief, tag):
                                setattr(brief, tag, value)
                    self.briefs.append(brief)
