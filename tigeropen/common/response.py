# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import json


class TigerResponse:
    def __init__(self):
        self.code = None
        self.message = None
        self.data = None

    def is_success(self):
        return self.code == 0

    def parse_response_content(self, response):
        if 'code' in response:
            self.code = response['code']
        if 'message' in response:
            self.message = response['message']
        if 'data' in response:
            self.data = response['data']
            if isinstance(self.data, str):
                self.data = json.loads(self.data)
        return response
