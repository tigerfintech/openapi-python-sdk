# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import SecurityType


class Contract(object):
    def __init__(self, symbol, currency, contract_id=None, sec_type=None, exchange=None, origin_symbol=None,
                 local_symbol=None, expiry=None, strike=None, put_call=None, multiplier=None, name=None,
                 short_margin=None, short_fee_rate=None, shortable=None, long_initial_margin=None,
                 long_maintenance_margin=None, contract_month=None, identifier=None):
        self.contract_id = contract_id
        self.symbol = symbol
        self.currency = currency
        self.sec_type = sec_type
        self.exchange = exchange
        self.origin_symbol = origin_symbol
        self.local_symbol = local_symbol
        self.expiry = expiry
        # 行权价
        self.strike = strike
        # 看跌/看涨
        self.put_call = put_call
        # 合约乘数
        self.multiplier = multiplier
        # 合约名称
        self.name = name
        # 做空保证金比例
        self.short_margin = short_margin
        # 做空费率
        self.short_fee_rate = short_fee_rate
        # 做空池剩余
        self.shortable = shortable
        # 做多初始保证金
        self.long_initial_margin = long_initial_margin
        # 做多维持保证金
        self.long_maintenance_margin = long_maintenance_margin
        # 合约月份
        self.contract_month = contract_month
        # 合约标识符
        self.identifier = identifier

    def __repr__(self):
        identifier = self.identifier if self.identifier else self.symbol
        if self.sec_type == SecurityType.FUT.value:
            return '%s/%s/%s/%s' % (identifier, self.sec_type, self.currency, self.exchange)
        else:
            return '%s/%s/%s' % (identifier, self.sec_type, self.currency)

    def is_cn_stock(self):
        """
        是否是A股
        :return:
        """
        return self.sec_type == 'STK' and (self.currency == 'CNH' or self.currency == 'CNY')
