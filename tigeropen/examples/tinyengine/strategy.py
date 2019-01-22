import numpy as np
from datetime import datetime

from tigeropen.common.consts import SecurityType, Currency


class TickerTrendUtil:
    def __init__(self):
        self.price_dict = {}

    def on_latest_price(self, symbol, latest_price):
        """
        093003 latest_price1
        093006 latest_price2
        093009 latest_price3

        return latest_price1 > latest_price2 < latest_price3
        """
        curr_price = self.price_dict.get(symbol)
        if curr_price:
            if len(curr_price) == 1:
                curr_price.append(latest_price)
                return False
            else:
                first = curr_price.pop(0)
                second = curr_price[0]

                curr_price.append(latest_price)

                return first > second < latest_price
        else:
            self.price_dict[symbol] = [latest_price]
            return False


class EMAUtil:
    def __init__(self, size):
        self.buf = np.zeros(size)
        self.maxsize = size
        self.head = 0
        self.sum = 0

    def get_osc(self):
        return self.sum / self.maxsize

    def on_new_value(self, value):
        tmp = self.buf[self.head]
        self.buf[self.head] = value
        self.sum += value - tmp
        self.head += 1
        if self.head >= self.maxsize:
            self.head -= self.maxsize


class Strategy(object):
    def __init__(self, push_client=None, trade_client=None, quote_client=None, context=None):

        self.push_client = push_client
        self.trade_client = trade_client
        self.quote_client = quote_client
        self.context = context

        self.time_zone = 'Asia/Shanghai'
        self.open_time = '093000'
        self.close_time = '150000'

        self.event_trigger = False

        # [event trigger] user customer lunch break
        self.lunch_break = datetime.strptime(str('113000'), '%H%M%S').time()
        self.afternoon_start = datetime.strptime(str('130000'), '%H%M%S').time()

        self.symbol_market_map = {'600029': {'security': SecurityType.STK, 'per_trade': 100},
                                  '600053': {'security': SecurityType.STK, 'per_trade': 100},
                                  '600604': {'security': SecurityType.STK, 'per_trade': 100}}
        self.symbol_set = set(self.symbol_market_map.keys())
        self.tick_util = TickerTrendUtil()

        self.short_min_ma = EMAUtil(10)
        self.long_min_ma = EMAUtil(20)

    def on_ticker(self, symbol, items, hour_trading):
        """
        run after subscribing market data
        """
        if hour_trading:
            return
        print(symbol, items, hour_trading)
        latest_price = dict(items).get('latest_price')
        if symbol in self.symbol_set:
            if self.tick_util.on_latest_price(symbol, latest_price):
                print('============= place order =============')
                contract = self.context.contract_map.get(symbol)
                symbol_market = self.symbol_market_map[symbol]
                self.trade_client.create_order(self.context.account, contract, 'BUY', 'MKT', symbol_market['per_trade'], limit_price=latest_price)

    def on_minute_bar(self, data):
        """
        start when time >= open_time
        stop when time <= end_time
        """
        if self.lunch_break <= data.dt.time() < self.afternoon_start:
            print('============= lunch break =============')
            return
        print(data.current(list(self.symbol_market_map.keys()), ['open', 'high', 'low', 'close', 'volume', 'time']))
        # history api is not recommended to use
        # data cannot be filled in
        print(data.history('600053', ['open', 'high', 'low', 'close', 'volume', 'time'], 10, '1m'))

    def before_trading_start(self):
        """
        run when starting engine
        """
        pass

    def dump(self):
        """
        run after close_time
        run before end
        """
        pass
