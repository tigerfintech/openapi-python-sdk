# -*- coding: utf-8 -*-
# 
# @Date    : 2021-04-16
# @Author  : sukai
import json
from tigeropen.common.response import TigerResponse


class QuoteGrabPermissionResponse(TigerResponse):
    def __init__(self):
        super(QuoteGrabPermissionResponse, self).__init__()
        self.is_master = False
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteGrabPermissionResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            self.is_master = data_json.get('is_master')
