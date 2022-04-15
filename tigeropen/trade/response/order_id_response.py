# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json
from tigeropen.common.response import TigerResponse


class OrderIdResponse(TigerResponse):
    def __init__(self):
        super(OrderIdResponse, self).__init__()
        self.order_id = None
        self.id = None
        self.sub_ids = None
        self._is_success = None
    
    def parse_response_content(self, response_content):
        response = super(OrderIdResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        
        if self.data:
            data_json = json.loads(self.data)
            if 'code' in data_json and data_json['code'] != '0':
                self.code = int(data_json['code'])
                if 'message' in data_json:
                    self.message = data_json['message']
            
            if 'orderId' in data_json:
                self.order_id = data_json['orderId']

            if 'id' in data_json:
                self.id = data_json['id']

            if 'subIds' in data_json:
                self.sub_ids = data_json['subIds']
