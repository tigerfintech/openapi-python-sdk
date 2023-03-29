# -*- coding: utf-8 -*-
# 
# @Date    : 2023/3/24
# @Author  : sukai
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.trade.domain.account import SegmentFundItem, SegmentFundAvailableItem


class SegmentFundAvailableResponse(TigerResponse):
    def __init__(self):
        super(SegmentFundAvailableResponse, self).__init__()
        self.data = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SegmentFundAvailableResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.data = [SegmentFundAvailableItem(**item) for item in string_utils.camel_to_underline_obj(self.data)]


class SegmentFundHistoryResponse(TigerResponse):
    def __init__(self):
        super(SegmentFundHistoryResponse, self).__init__()
        self.data = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SegmentFundHistoryResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.data = [SegmentFundItem(**item) for item in string_utils.camel_to_underline_obj(self.data)]


class SegmentFundTransferResponse(TigerResponse):
    def __init__(self):
        super(SegmentFundTransferResponse, self).__init__()
        self.data = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SegmentFundTransferResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.data = SegmentFundItem(**string_utils.camel_to_underline_obj(self.data))

        return response


class SegmentFundCancelResponse(TigerResponse):
    def __init__(self):
        super(SegmentFundCancelResponse, self).__init__()
        self.data = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(SegmentFundCancelResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            self.data = SegmentFundItem(**string_utils.camel_to_underline_obj(self.data))
