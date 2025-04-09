# -*- coding: utf-8 -*-
# 
# @Date    : 2021/12/2
# @Author  : sukai
MODEL_REPR = '{}({})'


class PortfolioAccount:
    """
    prime/paper account assets
    """
    def __init__(self, account, update_timestamp=None):
        """
        :param account:
        :param update_timestamp: asset update timestamp in milliseconds.
        """
        self.account = account
        self.update_timestamp = update_timestamp
        self._segments = dict()

    @property
    def segments(self):
        """account information by contract type
        :return: dict with two keys, 'S' for stocks， 'C' for commodity futures；
        """
        return self._segments

    def add_segment(self, segment):
        if segment.category not in self._segments:
            self._segments[segment.category] = segment
            return segment
        else:
            return self._segments.get(segment.category)

    def __repr__(self):
        d = {'account': self.account, 'update_timestamp': self.update_timestamp, 'segments': self.segments}
        return MODEL_REPR.format(self.__class__.__name__, d)


class Segment:
    def __init__(self):
        self.currency = None
        self.capability = None
        self.category = None
        self.cash_balance = float('inf')
        self.cash_available_for_trade = float('inf')
        self.cash_available_for_withdrawal = float('inf')
        self.gross_position_value = float('inf')
        self.equity_with_loan = float('inf')
        self.net_liquidation = float('inf')
        self.init_margin = float('inf')
        self.maintain_margin = float('inf')
        self.overnight_margin = float('inf')
        self.unrealized_pl = float('inf')
        self.realized_pl = float('inf')
        self.excess_liquidation = float('inf')
        self.overnight_liquidation = float('inf')
        self.buying_power = float('inf')
        self.leverage = float('inf')
        self._currency_assets = dict()
        self.consolidated_seg_types = list()
        self.locked_funds = float('inf')
        self.uncollected = float('inf')

    @property
    def currency_assets(self):
        return self._currency_assets

    def add_currency_asset(self, asset):
        if asset.currency not in self._currency_assets:
            self._currency_assets[asset.currency] = asset
            return asset
        else:
            return self._currency_assets.get(asset.currency)

    def __repr__(self):
        d = {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        d['currency_assets'] = self.currency_assets
        return MODEL_REPR.format(self.__class__.__name__, d)


class CurrencyAsset:
    def __init__(self):
        self.currency = None
        self.cash_balance = float('inf')
        self.cash_available_for_trade = float('inf')
        self.gross_position_value = float('inf')
        self.stock_market_value = float('inf')
        self.futures_market_value = float('inf')
        self.option_market_value = float('inf')
        self.unrealized_pl = float('inf')
        self.realized_pl = float('inf')

    @staticmethod
    def from_dict(d):
        currency_asset = CurrencyAsset()
        currency_asset.__dict__.update(d)
        return currency_asset

    def __repr__(self):
        return MODEL_REPR.format(self.__class__.__name__, self.__dict__)


class AggregateAsset:
    """
    """
    def __init__(self):
        # 基础币种
        self.currency = None
        # 现金余额
        self.cash_balance = float('inf')
        # 现金余额包括在途
        self.cash_balance_with_in_transit = float('inf')
        # 具有借贷价值资产
        self.equity_with_loan = float('inf')
        # 净清算价值
        self.net_liquidation = float('inf')
        # 初始保证金
        self.init_margin = float('inf')
        # 维持保证金
        self.maintain_margin = float('inf')
        # 外汇保证金
        self.trade_currency_margin = float('inf')
        # 日内风险度
        self.intraday_risk_ratio = float('inf')
        # 总市值
        self.gross_position_value = float('inf')
        # 股票持仓市值
        self.stock_market_value = float('inf')
        # 期权市值
        self.option_market_value = float('inf')
        # 可用剩余资产
        self.cash_available_for_trade = float('inf')
        # 可用现金值
        self.available_cash = float('inf')
        # 已锁定的剩余资产
        self.locked_funds = float('inf')
        # 锁定现金值
        self.locked_cash = float('inf')
        # 引用额度
        self.credit_limit = float('inf')
        # ee 剩余资产
        self.excess_equity = float('inf')
        # el 剩余流动资产
        self.excess_liquidity = float('inf')

    @staticmethod
    def from_dict(d):
        aggregate_asset = AggregateAsset()
        aggregate_asset.__dict__.update(d)
        return aggregate_asset

    def __repr__(self):
        return MODEL_REPR.format(self.__class__.__name__, self.__dict__)