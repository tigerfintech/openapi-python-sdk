# -*- coding: utf-8 -*-
"""
Created on 2018/10/31

@author: gaoan
"""
import pandas as pd

from tigeropen.common.response import TigerResponse

# 盘前盘后
HOUR_TRADING_COLUMNS = [
    'hour_trading_tag',
    'hour_trading_latest_price',
    'hour_trading_pre_close',
    'hour_trading_latest_time',
    'hour_trading_volume',
    'hour_trading_timestamp',
]
# 下一交易时段信息
NEXT_MARKET_STATUS_COLUMNS = [
    # 市场状态(US:开盘、收盘、盘前交易、盘后交易||CN/HK：开盘、收盘、午间休市)
    'next_market_status_tag',
    # 开始时间
    'next_market_status_begin_time',
]
# 拆合股
STOCK_SPLIT_COLUMNS = [
    # 执行日期 yyyy-MM-dd格式
    'stock_split_execute_date',
    # 公司行动后的因子
    'stock_split_to_factor',
    # 公司行动前的因子
    'stock_split_for_factor'
]
# 股权信息
STOCK_RIGHT_COLUMNS = [
    # 原股权代码
    'stock_right_symbol',
    # 股权代码
    'stock_right_rights_symbol',
    # 开始交易日期, YYYY-MM-dd格式，可能为空字符串
    'stock_right_first_dealing_date',
    # 最后交易日期, YYYY-MM-dd格式，可能为空字符串
    'stock_right_last_dealing_date'
]
# 股票代码变更
SYMBOL_CHANGE_COLUMNS = [
    # 新的股票代码
    'symbol_change_new_symbol',
    # 执行日期，yyyy-MM-dd格式
    'symbol_change_execute_date'
]
# 股票公告
STOCK_NOTICE_COLUMNS = [
    # 公告标题
    'stock_notice_title',
    # 公告内容
    'stock_notice_content',
    # 公告类型
    'stock_notice_type'
]

COLUMNS = ['symbol', 'market', 'exchange', 'sec_type', 'name', 'shortable', 'latest_price', 'pre_close',
           'adj_pre_close', 'trading_status', 'market_status', 'timestamp', 'latest_time',
           'open', 'high', 'low', 'volume', 'amount', 'ask_price', 'ask_size', 'bid_price', 'bid_size', 'change',
           'amplitude', 'halted', 'delay', 'float_shares', 'shares', 'eps', 'etf', 'listing_date', 'adr_rate'
           ] + HOUR_TRADING_COLUMNS + NEXT_MARKET_STATUS_COLUMNS + STOCK_SPLIT_COLUMNS + STOCK_RIGHT_COLUMNS \
          + SYMBOL_CHANGE_COLUMNS + STOCK_NOTICE_COLUMNS

DETAIL_FIELD_MAPPINGS = {'secType': 'sec_type', 'latestPrice': 'latest_price', 'preClose': 'pre_close',
                         'floatShares': 'float_shares', 'marketStatus': 'market_status', 'latestTime': 'latest_time',
                         'askPrice': 'ask_price', 'askSize': 'ask_size', 'bidPrice': 'bid_price', 'bidSize': 'bid_size',
                         'tradingStatus': 'trading_status', 'adjPreClose': 'adj_pre_close', 'adrRate': 'adr_rate',
                         'listingDate': 'listing_date', 'beginTime': 'begin_time',
                         'nextMarketStatus': 'next_market_status', 'hourTrading': 'hour_trading',
                         'stockSplit': 'stock_split', 'stockRight': 'stock_right', 'symbolChange': 'symbol_change',
                         'executeDate': 'execute_date', 'newSymbol': 'new_symbol', 'forFactor': 'for_factor',
                         'toFactor': 'to_factor', 'rightsSymbol': 'rights_symbol', 'stockNotice': 'stock_notice',
                         'firstDealingDate': 'first_dealing_date', 'lastDealingDate': 'last_dealing_date'
                         }

SUB_FIELDS = {
    # 下一交易时段信息
    'next_market_status',
    # 盘前盘后信息
    'hour_trading',
    # 拆合股
    'stock_split',
    # 股权信息
    'stock_right'
    # 股票代码变更
    'symbol_change',
    # 公告
    'stock_notice'
}


class StockDetailsResponse(TigerResponse):
    def __init__(self):
        super(StockDetailsResponse, self).__init__()
        self.details = None
        self._is_success = None

    def parse_response_content(self, response_content):
        response = super(StockDetailsResponse, self).parse_response_content(response_content)
        if 'is_success' in response:
            self._is_success = response['is_success']
        if not self.data:
            return
        detail_data = []
        for item in self.data.get('items', {}):
            item_values = dict()
            for key, value in item.items():
                if value is None:
                    continue
                tag = self._key_to_tag(key)
                if tag in SUB_FIELDS:
                    for sub_k, sub_v in value.items():
                        sub_tag = self._key_to_tag(sub_k)
                        item_values[self._join_tag(tag, sub_tag)] = sub_v
                else:
                    item_values[tag] = value

            detail_data.append([item_values.get(tag) for tag in COLUMNS])

        self.details = pd.DataFrame(detail_data, columns=COLUMNS)

    @classmethod
    def _key_to_tag(cls, k):
        return DETAIL_FIELD_MAPPINGS[k] if k in DETAIL_FIELD_MAPPINGS else k

    @classmethod
    def _join_tag(cls, tag, sub_tag):
        return '_'.join((tag, sub_tag))
