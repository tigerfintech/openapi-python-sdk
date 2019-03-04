import numpy as np


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

        # [subscribe symbols][necessary setting]
        self.context.subscribe('AAPL')
        # self.context.subscribe('01810')
        # [strategy related][not necessary setting] local vars with different strategy
        self.symbol_set = set(self.context.subscribed_symbols)
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
                print('============= create order =============')
                contract = self.context.contract_map.get(symbol)
                self.trade_client.create_order(self.context.account, contract, 'BUY', 'MKT', 100, limit_price=latest_price)

    def before_trading_start(self, data):
        """
        run when starting engine
        """
        pass

    def dump(self):
        """
        dump some data which user needs
        run after close_time
        run before end
        """
        pass