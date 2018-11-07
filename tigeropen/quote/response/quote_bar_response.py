# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json
import six

from tigeropen.common.util.string_utils import get_string
from tigeropen.quote.domain.bar import Bar
from tigeropen.common.response import TigerResponse

BAR_FIELD_MAPPINGS = {'avgPrice': 'avg_price'}


class QuoteBarResponse(TigerResponse):
    def __init__(self):
        super(QuoteBarResponse, self).__init__()
        self.bars = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteBarResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    bar = Bar()
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
                        tag = BAR_FIELD_MAPPINGS[key] if key in BAR_FIELD_MAPPINGS else key
                        if hasattr(bar, tag):
                            setattr(bar, tag, value)
                    self.bars.append(bar)
