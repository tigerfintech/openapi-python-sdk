from functools import partial


class Portfolio:
    def __init__(self, context):
        self.context = context

    @property
    def cash(self):
        return self.context.asset_manager.summary.available_funds

    @property
    def positions_value(self):
        return self.context.asset_manager.summary.gross_position_value

    @property
    def portfolio_value(self):
        return self.context.asset_manager.summary.gross_position_value + self.context.asset_manager.summary.available_funds

    @property
    def positions(self):
        return self.context.position_manager


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
