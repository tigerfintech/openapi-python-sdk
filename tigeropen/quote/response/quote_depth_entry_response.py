# -*- coding: utf-8 -*-
import pandas as pd
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string


class DepthEntryResponse(TigerResponse):
    def __init__(self):
        super(DepthEntryResponse, self).__init__()
        self.depth_entry = []
        self._is_success = None

    def parse_response_content(self, response_content):
        """
        :return: pandas.DataFrame
            symbol    ask_price ask_volume ask_count   bid_price bid_volume bid_count
            SYMBOL1   卖1价      卖1股数     卖1订单数    买1价     买1股数     买1订单数
            SYMBOL1   卖2价      卖2股数     卖2订单数    买2价     买2股数     买2订单数
               .
               .
            SYMBOL1   卖10价     卖10股数    卖10订单数   买10价    买10股数    买10订单数


            SYMBOL2   卖1价      卖1股数     卖1订单数    买1价     买1股数     买1订单数
            SYMBOL2   卖2价      卖2股数     卖2订单数    买2价     买2股数     买2订单数
               .
               .
            SYMBOL2   卖10价     卖10股数    卖10订单数  买10价    买10股数     买10订单数
        """
        response = super(DepthEntryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            result = list()
            for item in self.data:
                symbol = get_string(item.get('symbol'))
                asks = pd.DataFrame(item.get('asks', []))[['count', 'volume', 'price']].add_prefix('ask_')
                bids = pd.DataFrame(item.get('bids', []))[['price', 'volume', 'count']].add_prefix('bid_')
                merged_data = pd.concat([asks, bids], axis=1)
                merged_data.insert(loc=0, column='symbol', value=symbol)
                result.append(merged_data)
            self.depth_entry = pd.concat(result)
            return self.depth_entry


