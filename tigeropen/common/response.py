# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class TigerResponse(object):
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
        return response
