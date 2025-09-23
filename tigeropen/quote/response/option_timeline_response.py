# -*- coding: utf-8 -*-


import pandas as pd

from tigeropen.common.consts import Market
from tigeropen.common.response import TigerResponse
from tigeropen.common.util.common_utils import get_tz_by_market
from tigeropen.common.util.contract_utils import get_option_identifier, is_hk_option_underlying_symbol
from tigeropen.common.util.string_utils import camel_to_underline_obj


class OptionTimelineResponse(TigerResponse):
    def __init__(self):
        super(OptionTimelineResponse, self).__init__()
        self.result = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(OptionTimelineResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            timeline_items = []
            for symbol_item in self.data:
                identifier = symbol_item.get('identifier')
                underlying_symbol = symbol_item.get('symbol')
                expiry = symbol_item.get('expiry')
                strike = symbol_item.get('strike')
                put_call = symbol_item.get('right').upper()
                pre_close = symbol_item.get('preClose')
                if not identifier:
                    if is_hk_option_underlying_symbol(underlying_symbol):
                        tz = get_tz_by_market(Market.HK)
                    else:
                        tz = get_tz_by_market(Market.US)
                    expiration = pd.Timestamp(expiry, unit='ms', tzinfo=tz).date().strftime("%Y%m%d")
                    identifier = get_option_identifier(underlying_symbol, expiration, put_call, strike)
                option_info = {
                    'identifier': identifier,
                    'symbol': underlying_symbol,
                    'expiry': expiry,
                    'put_call': put_call,
                    'strike': strike,
                    'pre_close': pre_close,
                }
                minutes = symbol_item.get('minutes')
                if minutes:
                    for item in minutes:
                        item_values = dict(option_info)
                        item_values.update(camel_to_underline_obj(item))
                        timeline_items.append(item_values)

            self.result = pd.DataFrame(timeline_items)


