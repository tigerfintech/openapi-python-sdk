# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class Contract(object):
    def __init__(self, symbol, currency, contract_id=None, sec_type=None, exchange=None, origin_symbol=None,
                 local_symbol=None, expiry=None, strike=None, put_call=None, multiplier=None):
        self.contract_id = contract_id
        self.symbol = symbol
        self.currency = currency
        self.sec_type = sec_type
        self.exchange = exchange
        self.origin_symbol = origin_symbol
        self.local_symbol = local_symbol
        self.expiry = expiry
        self.strike = strike
        self.put_call = put_call
        self.multiplier = multiplier

    def __repr__(self):
        if self.symbol:
            if self.origin_symbol is not None:
                return self.origin_symbol
            elif self.contract_id:
                return '%s/%s/%s/%d' % (self.symbol, self.sec_type, self.currency, self.contract_id)
            else:
                return '%s/%s/%s' % (self.symbol, self.sec_type, self.currency)
        else:
            return '%d' % (self.contract_id,)

    def is_cn_stock(self):
        """
        是否是A股
        :return:
        """
        return self.sec_type == 'STK' and (self.currency == 'CNH' or self.currency == 'CNY')
