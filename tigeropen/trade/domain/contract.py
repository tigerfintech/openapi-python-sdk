# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
from tigeropen.common.consts import SecurityType
from tigeropen.common.util.common_utils import get_enum_value


class Contract:
    def __init__(self, symbol=None, currency=None, contract_id=None, sec_type=None, exchange=None, origin_symbol=None,
                 local_symbol=None, expiry=None, strike=None, put_call=None, multiplier=None, name=None,
                 short_margin=None, short_fee_rate=None, shortable=None, shortable_count=None, long_initial_margin=None,
                 long_maintenance_margin=None, contract_month=None, identifier=None, primary_exchange=None,
                 market=None, min_tick=None, trading_class=None, status=None, continuous=None, trade=None,
                 marginable=None, close_only=None,
                 last_trading_date=None, first_notice_date=None, last_bidding_close_time=None):
        self.contract_id = contract_id
        self.symbol = symbol
        self.currency = get_enum_value(currency)
        self.sec_type = get_enum_value(sec_type)
        self.exchange = exchange
        self.origin_symbol = origin_symbol
        self.local_symbol = local_symbol
        # 到期日
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
        self.shortable_count = shortable_count
        # 做多初始保证金
        self.long_initial_margin = long_initial_margin
        # 做多维持保证金
        self.long_maintenance_margin = long_maintenance_margin
        # 合约月份
        self.contract_month = contract_month
        # 合约标识符
        self.identifier = identifier
        # 股票上市交易所
        self.primary_exchange = primary_exchange
        # 市场
        self.market = market
        # 最小报价单位
        self.min_tick = min_tick
        # 合约的交易级别名称
        self.trading_class = trading_class
        # 状态
        self.status = status
        # is marginable
        self.marginable = marginable
        # is tradeable
        self.trade = trade
        # is only closed a position allowed
        self.close_only = close_only
        # 期货专有，是否连续合约
        self.continuous = continuous
        # 期货专有，最后交易日
        self.last_trading_date = last_trading_date
        # 期货专有，第一通知日，合约在第一通知日后无法开多仓. 已有的多仓会在第一通知日之前（通常为前三个交易日）被强制平仓
        self.first_notice_date = first_notice_date
        # 期货专有，竞价截止时间
        self.last_bidding_close_time = last_bidding_close_time

    @property
    def right(self):
        return self.put_call

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
