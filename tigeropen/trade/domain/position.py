# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class Position:
    def __init__(self, account, contract, quantity=0, average_cost=None, market_price=None, market_value=None,
                 realized_pnl=None, unrealized_pnl=None, position_scale=None, **kwargs):
        """
        - account: 对应的账户ID
        - contract: 合约对象
        - quantity: 合约数量
        - average_cost: 含佣金的平均成本
        - market_price: 市价
        - market_value: 市值
        - realized_pnl: 已实现盈亏
        - unrealized_pnl: 未实现盈亏
        """
        self.account = account
        self.contract = contract
        self.quantity = quantity
        self.average_cost = average_cost
        self.average_cost_by_average = kwargs.get('average_cost_by_average', None)
        self.average_cost_of_carry = kwargs.get('average_cost_of_carry', None)
        self.market_price = market_price
        self.market_value = market_value
        self.realized_pnl = realized_pnl
        self.realized_pnl_by_average = kwargs.get('realized_pnl_by_average', None)
        self.unrealized_pnl = unrealized_pnl
        self.unrealized_pnl_by_average = kwargs.get('unrealized_pnl_by_average', None)
        self.position_scale = position_scale
        self.unrealized_pnl_percent = kwargs.get('unrealized_pnl_percent', None)
        self.unrealized_pnl_percent_by_average = kwargs.get('unrealized_pnl_percent_by_average', None)
        self.mm_value = kwargs.get('mm_value', None)
        self.mm_percent = kwargs.get('mm_percent', None)
        self.position_qty = kwargs.get('position_qty', self.quantity)
        self.salable_qty = kwargs.get('salable_qty', None)
        self.salable = self.saleable = self.salable_qty  # 兼容之前字段
        self.today_pnl = kwargs.get('today_pnl', None)
        self.today_pnl_percent = kwargs.get('today_pnl_percent', None)
        self.yesterday_pnl = kwargs.get('yesterday_pnl', None)
        self.last_close_price = kwargs.get('last_close_price', None)
        self.unrealized_pnl_by_cost_of_carry = kwargs.get('unrealized_pnl_by_cost_of_carry', None)
        self.unrealized_pnl_percent_by_cost_of_carry = kwargs.get('unrealized_pnl_percent_by_cost_of_carry', None)
        self.is_level0_price = kwargs.get('is_level0_price', None)

    def __repr__(self):
        return f"Position({self.__dict__})"

    
    def __str__(self):
        return self.__repr__()
    
    def to_dict(self):
        """
        Creates a dictionary representing the state of this position.
        Returns a dict object of the form:
        """
        return {
            'contract': self.contract,
            'quantity': self.quantity,
            'average_cost': self.average_cost,
            'market_price': self.market_price
        }


class TradableQuantityItem:
    def __init__(self, tradable_quantity=0, financing_quantity=0, position_quantity=0, tradable_position_quantity=0):
        self.tradable_quantity = tradable_quantity
        self.financing_quantity = financing_quantity
        self.position_quantity = position_quantity
        self.tradable_position_quantity = tradable_position_quantity

    def __repr__(self):
        return 'TradableQuantityItem<{0}>'.format(self.__dict__)