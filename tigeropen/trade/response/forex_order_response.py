# -*- coding: utf-8 -*-
# 
# @Date    : 2023/3/28
# @Author  : sukai
from tigeropen.common.response import TigerResponse
from tigeropen.trade.response.orders_response import OrdersResponse


class ForexOrderResponse(TigerResponse):
    def __init__(self):
        super(ForexOrderResponse, self).__init__()
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(ForexOrderResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if self.data:
            self.data = OrdersResponse.parse_order(self.data)

