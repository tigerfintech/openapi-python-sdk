# -*- coding: utf-8 -*-
# 
# @Date    : 2021-04-16
# @Author  : sukai
import json
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils


class QuoteGrabPermissionResponse(TigerResponse):
    def __init__(self):
        super(QuoteGrabPermissionResponse, self).__init__()
        self.permissions = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteGrabPermissionResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.permissions = string_utils.camel_to_underline_obj(self.data)
