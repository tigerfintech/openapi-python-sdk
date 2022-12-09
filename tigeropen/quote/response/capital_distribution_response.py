# -*- coding: utf-8 -*-
# 
# @Date    : 2022-12-09
# @Author  : sukai
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.quote.domain.capital_distribution import CapitalDistribution


class CapitalDistributionResponse(TigerResponse):
    def __init__(self):
        super().__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super().parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            capital_distribution = CapitalDistribution()
            capital_distribution.__dict__ = string_utils.camel_to_underline_obj(self.data)
            self.result = capital_distribution