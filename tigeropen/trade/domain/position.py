# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""


class Position(object):
    def __init__(self, account, contract, quantity=0, average_cost=None, market_price=None, market_value=None,
                 realized_pnl=None, unrealized_pnl=None):
        self.account = account
        self.contract = contract
        self.quantity = quantity
        self.average_cost = average_cost
        self.market_price = market_price
        self.market_value = market_value
        self.realized_pnl = realized_pnl
        self.unrealized_pnl = unrealized_pnl
    
    def __repr__(self):
        template = "contract: {contract}, quantity: {quantity}, average_cost: {average_cost}, " \
                   "market_price: {market_price}"
        return template.format(
            contract=self.contract,
            quantity=self.quantity,
            average_cost=self.average_cost,
            market_price=self.market_price
        )
    
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
