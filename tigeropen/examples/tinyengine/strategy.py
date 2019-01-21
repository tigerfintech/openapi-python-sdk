from tigeropen.common.consts import SecurityType, Currency


class Strategy(object):
    def __init__(self, push_client=None, trade_client=None, quote_client=None, context=None):

        self.push_client = push_client
        self.trade_client = trade_client
        self.quote_client = quote_client
        self.context = context

        self.open_time = '093000'
        self.close_time = '150000'
        self.time_zone = 'Asia/Shanghai'
        self.event_trigger = True

        self.symbol_market_map = {'600029': {'security': SecurityType.STK, 'currency': Currency.CNH},
                                  '600053': {'security': SecurityType.STK, 'currency': Currency.CNH},
                                  '600604': {'security': SecurityType.STK, 'currency': Currency.CNH}}

    def on_ticker(self, symbol, items, hour_trading):
        """
        run after subscribing market data
        """
        if hour_trading:
            return
        print(symbol, items, hour_trading)

    def on_minute_bar(self, data):
        """
        start when time >= open_time
        stop when time <= end_time
        """
        print(data.current(list(self.symbol_market_map.keys()), ['open', 'high', 'low', 'close', 'volume', 'time']))

        print(data.history('600053', ['open', 'high', 'low', 'close', 'volume', 'time'], 10, '1m'))

    def before_trading_start(self):
        """
        run when starting engine
        """
        pass

    def dump(self):
        """
        run before end
        """
        pass
