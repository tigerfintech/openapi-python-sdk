# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

COLUMNS = ['start', 'end', 'trading', 'bidding', 'zone']


class FutureTradingTimesResponse(TigerResponse):
    def __init__(self):
        super(FutureTradingTimesResponse, self).__init__()
        self.trading_times = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(FutureTradingTimesResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            zone = self.data.get('timeSection')
            bidding_times = self.data.get('biddingTimes')
            trading_times = self.data.get('tradingTimes')

            time_items = []
            if bidding_times:
                for item in bidding_times:
                    start = item.get('start')
                    end = item.get('end')
                    time_items.append([start, end, False, True, zone])
            if trading_times:
                for item in trading_times:
                    start = item.get('start')
                    end = item.get('end')
                    time_items.append([start, end, True, False, zone])

            self.trading_times = pd.DataFrame(time_items, columns=COLUMNS)
