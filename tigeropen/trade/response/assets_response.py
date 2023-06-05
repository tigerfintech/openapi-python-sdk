# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.response import TigerResponse
from tigeropen.trade.domain.account import PortfolioAccount
from tigeropen.common.util.string_utils import camel_to_underline

ACCOUNT_FIELD_MAPPINGS = {'sMA': 'sma', 'updateTime': 'timestamp', 'realizedPnL': 'realized_pnl',
                          'unrealizedPnL': 'unrealized_pnl', 'regTMargin': 'regt_margin', 'regTEquity': 'regt_equity',
                          'cashValue': 'cash', 'initMarginReq': 'initial_margin_requirement',
                          'maintMarginReq': 'maintenance_margin_requirement', 'futuresPnl': 'futures_pnl'}

MARKET_VALUE_FIELD_MAPPINGS = {'updateTime': 'timestamp'}


class AssetsResponse(TigerResponse):
    def __init__(self):
        super(AssetsResponse, self).__init__()
        self.assets = []
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(AssetsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']

        if self.data:
            if 'items' in self.data:
                for item in self.data['items']:
                    account = item['account']
                    asset = PortfolioAccount(account)
                    summary = asset.summary

                    for key, value in item.items():
                        if value is None:
                            continue
                        tag = ACCOUNT_FIELD_MAPPINGS[key] if key in ACCOUNT_FIELD_MAPPINGS else camel_to_underline(key)
                        if hasattr(summary, tag):
                            setattr(summary, tag, value)
                        elif 'market_values' == tag:
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    currency = sub_key
                                    market_value = asset.market_value(currency=currency)
                                    self._parse_market_value(market_value, sub_value)
                            elif isinstance(value, list):
                                for sub_value in value:
                                    currency = sub_value.get('currency')
                                    if not currency:
                                        continue
                                    market_value = asset.market_value(currency=currency)
                                    self._parse_market_value(market_value, sub_value)
                        elif 'segments' == tag and value:
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    segment_name = sub_key
                                    segment = asset.segment(segment_name=segment_name)
                                    self._parse_segment(segment, sub_value)
                            elif isinstance(value, list):
                                for sub_value in value:
                                    segment_name = sub_value.get('category')
                                    if not segment_name:
                                        continue
                                    segment = asset.segment(segment_name=segment_name)
                                    self._parse_segment(segment, sub_value)

                    self.assets.append(asset)

    @staticmethod
    def _parse_segment(segment, sub_value):
        for segment_key, segment_value in sub_value.items():
            if segment_value is None:
                continue
            if segment_key in ACCOUNT_FIELD_MAPPINGS:
                sub_tag = ACCOUNT_FIELD_MAPPINGS[segment_key]
            else:
                sub_tag = camel_to_underline(segment_key)
            setattr(segment, sub_tag, segment_value)

    @staticmethod
    def _parse_market_value(market_value, sub_value):
        for mv_key, mv_value in sub_value.items():
            if mv_value is None:
                continue
            if mv_key in ACCOUNT_FIELD_MAPPINGS:
                sub_tag = ACCOUNT_FIELD_MAPPINGS[mv_key]
            else:
                sub_tag = camel_to_underline(mv_key)
            if hasattr(market_value, sub_tag):
                setattr(market_value, sub_tag, mv_value)
