from functools import partial
from .client import trade_client
from .setting import IS_PAPER


class Portfolio:
    def __init__(self, context):
        self.context = context

    @property
    def cash(self):
        if IS_PAPER:
            assets = trade_client.get_assets()
            if assets:
                return assets[0].summary.cash
        else:
            return self.context.asset_manager.summary.cash

    @property
    def positions_value(self):
        if IS_PAPER:
            assets = trade_client.get_assets()
            if assets:
                return assets[0].summary.gross_position_value
        else:
            return self.context.asset_manager.summary.gross_position_value

    @property
    def portfolio_value(self):
        if IS_PAPER:
            assets = trade_client.get_assets()
            if assets:
                return assets[0].summary.net_liquidation
        return self.context.asset_manager.summary.net_liquidation

    @property
    def positions(self):
        if IS_PAPER:
            positions = trade_client.get_positions()
            return {position.contract.symbol: position for position in positions}
        else:
            return self.context.position_manager

    def __repr__(self):
        return '<Portfolio: net_liquidation: %s, cash: %s, positions_value: %s>' \
               % (self.portfolio_value, self.cash, self.positions_value)


class CompatibleStrategy:
    """与量化平台兼容的策略"""
    def __init__(self, push_client=None, trade_client=None, quote_client=None, context=None):
        self.push_client = push_client
        self.trade_client = trade_client
        self.quote_client = quote_client
        self.context = context

        self.context.portfolio = Portfolio(context)

        self.initialize = self.noop
        self.before_trading_start = self.noop
        self.handle_data = self.noop

        from . import strategy_event_trigger
        if hasattr(strategy_event_trigger, 'initialize'):
            self.initialize = partial(strategy_event_trigger.initialize, context=self.context)
        if hasattr(strategy_event_trigger, 'before_trading_start'):
            self.before_trading_start = partial(strategy_event_trigger.before_trading_start, context=self.context)
        if hasattr(strategy_event_trigger, 'handle_data'):
            self.handle_data = partial(strategy_event_trigger.handle_data, context=self.context)

    def noop(self, *args, **kwargs):
        pass
