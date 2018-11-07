# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json
import six

from tigeropen.common.util.string_utils import get_string
from tigeropen.quote.domain.timeline import Timeline
from tigeropen.common.response import TigerResponse

TIMELINE_FIELD_MAPPINGS = {'time': 'latest_time', 'avgPrice': 'avg_price'}


class QuoteTimelineResponse(TigerResponse):
    def __init__(self):
        super(QuoteTimelineResponse, self).__init__()
        self.pre_market = []
        self.regular = []
        self.after_hours = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(QuoteTimelineResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:  # regular
                regular_timelines = data_json['items'][0]['items']  # TODO
                for item in regular_timelines:
                    timeline = Timeline()
                    for key, value in item.items():
                        if value is None:
                            continue
                        if isinstance(value, six.string_types):
                            value = get_string(value)
                        tag = TIMELINE_FIELD_MAPPINGS[key] if key in TIMELINE_FIELD_MAPPINGS else key
                        if hasattr(timeline, tag):
                            setattr(timeline, tag, value)
                    self.regular.append(timeline)
