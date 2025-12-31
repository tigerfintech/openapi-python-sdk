# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.consts import Market
from tigeropen.common.response import TigerResponse
from tigeropen.common.util import string_utils
from tigeropen.common.util.common_utils import get_tz_by_market
from tigeropen.common.util.contract_utils import get_option_identifier, is_hk_option_underlying_symbol

BRIEF_FIELD_MAPPINGS = {
    'right': 'put_call',
    'openInt': 'open_interest'
}


class OptionBriefsResponse(TigerResponse):
    def __init__(self):
        super(OptionBriefsResponse, self).__init__()
        self.briefs = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionBriefsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data and isinstance(self.data, list):
            brief_data = []
            for item in self.data:
                item_values = {}
                for key, value in item.items():
                    if value is None:
                        continue
                    if key == 'right' and value:
                        value = value.upper()
                    item_values[key] = value
                if 'identifier' not in item_values:
                    underlying_symbol = item_values.get('symbol')
                    expiry = item_values.get('expiry')
                    strike = float(item_values.get('strike')) if item_values.get('strike') is not None else None
                    put_call = item_values.get('right')
                    if underlying_symbol and expiry and strike is not None and put_call:
                        if is_hk_option_underlying_symbol(underlying_symbol):
                            tz = get_tz_by_market(Market.HK)
                        else:
                            tz = get_tz_by_market(Market.US)
                        expiry = pd.Timestamp(expiry, unit='ms', tzinfo=tz).date().strftime("%Y%m%d")
                        item_values['identifier'] = get_option_identifier(underlying_symbol, expiry, put_call, strike)

                brief_data.append(item_values)

            if brief_data:
                df = pd.DataFrame(brief_data)
            else:
                df = pd.DataFrame()

            if not df.empty:
                field_mapping = {item: string_utils.camel_to_underline(item) for item in df.columns}
                field_mapping.update(BRIEF_FIELD_MAPPINGS)
                df = df.rename(columns=field_mapping)
                columns = list(df.columns)
                self.briefs = df.loc[:, columns]
            else:
                self.briefs = pd.DataFrame()
