# -*- coding: utf-8 -*-
# 
# @Date    : 2022-12-09
# @Author  : sukai
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.quote.domain.stock_broker import StockBroker, LevelBroker, Broker


class StockBrokerResponse(TigerResponse):
    def __init__(self):
        super().__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data = string_utils.camel_to_underline_obj(self.data)
            stock_broker = StockBroker()
            stock_broker.symbol = data.get('symbol')
            if data.get('bid_broker'):
                stock_broker.bid_broker = self._build_level_broker(data.get('bid_broker'))
            if data.get('ask_broker'):
                stock_broker.ask_broker = self._build_level_broker(data.get('ask_broker'))
            self.result = stock_broker

    def _build_level_broker(self, level_data):
        level_broker_list = list()
        for level_data in level_data:
            level_broker = LevelBroker()
            level_broker.level = level_data.get('level')
            level_broker.price = level_data.get('price')
            level_broker.broker_count = level_data.get('broker_count')
            if level_data.get('broker'):
                broker_list = list()
                for broker_data in level_data.get('broker'):
                    broker = Broker()
                    broker.__dict__ = broker_data
                    broker_list.append(broker)
                level_broker.broker = broker_list
            level_broker_list.append(level_broker)
        return level_broker_list
