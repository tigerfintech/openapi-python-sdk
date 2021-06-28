# -*- coding: utf-8 -*-
# 
# @Date    : 2021-04-16
# @Author  : sukai
import json
from tigeropen.common.response import TigerResponse


class QuoteGrabPermissionResponse(TigerResponse):
    def __init__(self):
        super(QuoteGrabPermissionResponse, self).__init__()
        self.permissions = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteGrabPermissionResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        self.permissions = self.data
