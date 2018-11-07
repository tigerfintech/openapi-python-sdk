# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import get_string
from tigeropen.trade.domain.profile import AccountProfile


class ProfilesResponse(TigerResponse):
    def __init__(self):
        super(ProfilesResponse, self).__init__()
        self.profiles = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(ProfilesResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            data_json = json.loads(self.data)
            if 'items' in data_json:
                for item in data_json['items']:
                    account, capability, status = None, None, None
                    for key, value in item.items():
                        if value is None:
                            continue
                        if key == 'account':
                            account = get_string(value)
                        elif key == 'capability':
                            capability = get_string(value)
                        elif key == 'status':
                            status = get_string(value)
                    profile = AccountProfile(account, capability, status)
                    self.profiles.append(profile)
