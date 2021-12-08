# -*- coding: utf-8 -*-
#
# @Date    : 2021/12/2
# @Author  : sukai

from tigeropen.common.response import TigerResponse
from tigeropen.trade.domain.prime_account import PortfolioAccount, Segment, CurrencyAsset
from tigeropen.common.util.string_utils import camel_to_underline, camel_to_underline_obj


class PrimeAssetsResponse(TigerResponse):
    def __init__(self):
        super(PrimeAssetsResponse, self).__init__()
        self.assets = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(PrimeAssetsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            assets = PortfolioAccount(self.data.get('accountId'), self.data.get('updateTimestamp'))

            for segment_data in self.data.get('segments', list()):
                segment = Segment()
                for key, value in segment_data.items():
                    if key == 'currencyAssets':
                        currency_assets = camel_to_underline_obj(value)
                        [segment.add_currency_asset(CurrencyAsset.from_dict(i)) for i in currency_assets]
                    else:
                        setattr(segment, camel_to_underline(key), value)
                assets.add_segment(segment)
            self.assets = assets


