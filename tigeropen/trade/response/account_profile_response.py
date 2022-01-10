# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import json

from tigeropen.common.response import TigerResponse
from tigeropen.common.util.string_utils import camel_to_underline_obj
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
                    data_dict = camel_to_underline_obj(item)
                    profile = AccountProfile(account=data_dict.get('account'), capability=data_dict.get('capability'),
                                             status=data_dict.get('status'), account_type=data_dict.get('account_type'))
                    self.profiles.append(profile)
