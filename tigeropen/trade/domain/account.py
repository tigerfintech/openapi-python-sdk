# -*- coding: utf-8 -*-
"""
Created on 2018/9/20

@author: gaoan
"""
import logging
from collections import defaultdict


class Account(object):
    """
    The account object tracks information about the trading account. The
    values are updated as the algorithm runs and its keys remain unchanged.
    If connected to a broker, one can update these values with the trading
    account values as reported by the broker.
    """

    def __init__(self):
        self.settled_cash = float('inf')
        self.accrued_interest = float('inf')
        self.accrued_cash = float('inf')
        self.accrued_dividend = float('inf')
        self.buying_power = float('inf')
        self.equity_with_loan = float('inf')
        self.gross_position_value = float('inf')
        self.regt_equity = float('inf')
        self.regt_margin = float('inf')
        self.initial_margin_requirement = float('inf')
        self.maintenance_margin_requirement = float('inf')
        self.available_funds = float('inf')
        self.excess_liquidity = float('inf')
        self.cushion = float('inf')
        self.day_trades_remaining = float('inf')
        self.leverage = float('inf')
        self.net_leverage = float('inf')
        self.net_liquidation = float('inf')
        self.cash = float('inf')
        self.sma = float('inf')
        self.currency = None
        self.timestamp = None

    def __repr__(self):
        return "Account({0})".format(self.__dict__)


class MarketValue(object):
    def __init__(self):
        self.currency = None
        self.net_liquidation = float('inf')
        self.cash_balance = float('inf')
        self.total_cash_balance = float('inf')
        self.forex_cash_balance = float('inf')
        self.net_interest = float('inf')
        self.stock_market_value = float('inf')
        self.option_market_value = float('inf')
        self.future_option_market_value = float('inf')
        self.mutual_fund_market_value = float('inf')
        self.money_market_fund_value = float('inf')
        self.corporate_bond_value = float('inf')
        self.treasury_bond_value = float('inf')
        self.treasury_bill_value = float('inf')
        self.warrant_value = float('inf')
        self.future_pnl = float('inf')
        self.unrealized_pnl = float('inf')
        self.realized_pnl = float('inf')
        self.exchange_rate = float('inf')
        self.cash_cum_qty = float('inf')
        self.net_dividend = float('inf')
        self.timestamp = None

    def __repr__(self):
        return "MarketValue({0})".format(self.__dict__)


class PortfolioAccount(object):
    def __init__(self, account):
        self._account = account
        self._summary = Account()
        self._segments = defaultdict(Account)
        self._market_values = defaultdict(MarketValue)

    @property
    def account(self):
        return self._account

    @property
    def summary(self):
        return self._summary

    def segment(self, segment_name):
        if segment_name not in ('C', 'S', 'F'):
            logging.info("unknown segment %s", segment_name)
        if segment_name in self._segments:  # C, S, F
            return self._segments.get(segment_name)
        else:
            segment = Account()
            self._segments[segment_name] = segment
            return segment

    @property
    def segments(self):
        return self._segments

    def market_value(self, currency):
        if currency in self._market_values:
            return self._market_values.get(currency)
        else:
            market_value = MarketValue()
            self._market_values[currency] = market_value
            return market_value

    @property
    def market_values(self):
        return self._market_values
