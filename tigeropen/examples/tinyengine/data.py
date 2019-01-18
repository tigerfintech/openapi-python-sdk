from datetime import datetime, timedelta
import pandas as pd


COLUMNS = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']


class BarManager(object):
    def __init__(self):
        self.curr_bar = None
        self.last_bar = None
        self.data_bar = pd.DataFrame(columns=COLUMNS)
        # self.data_bar.set_index('time')
        self.last_minute = None


class BarUtil(object):
    def __init__(self):
        self.bar_manager = {}

    def on_data(self, symbol, items):
        price_dict = dict(items)
        latest_price = price_dict.get('latest_price')
        volume = price_dict.get('volume')
        timestamp = price_dict.get('latest_time')

        curr_minute = datetime.fromtimestamp(timestamp / 1000).minute

        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager:
            if curr_minute != curr_bar_manager.last_minute:
                curr_bar_manager.last_bar = curr_bar_manager.curr_bar.copy()
                # curr_bar_manager.data_bar.append(curr_bar_manager.curr_bar.copy(), ignore_index=True)
                curr_bar_manager.curr_bar = pd.Series([symbol, timestamp, latest_price, latest_price, latest_price,
                                                       latest_price, volume], index=COLUMNS)
                curr_bar_manager.last_minute = curr_minute
            else:
                # curr_bar_manager.curr_bar.time = timestamp
                curr_bar_manager.curr_bar.high = max(curr_bar_manager.curr_bar.high, latest_price)
                curr_bar_manager.curr_bar.low = min(curr_bar_manager.curr_bar.high, latest_price)
                curr_bar_manager.curr_bar.close = latest_price
                curr_bar_manager.curr_bar.volume += volume
        else:
            curr_bar_manager = BarManager()
            self.bar_manager[symbol] = curr_bar_manager
            curr_bar_manager.curr_bar = pd.Series([symbol, timestamp, latest_price, latest_price, latest_price,
                                                   latest_price, volume], index=COLUMNS)
            curr_bar_manager.last_bar = curr_bar_manager.curr_bar.copy()
            curr_bar_manager.last_minute = curr_minute

    def set_data(self, data):
        for curr_bar_manager in self.bar_manager.values():
            curr_bar = curr_bar_manager.last_bar.copy()
            curr_bar.name = data.dt
            curr_bar.time = data.dt.timestamp()
            curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar)

    def get_last_bar(self, symbol, fields):
        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager:
            return curr_bar_manager.last_bar[fields]
        else:
            return None

    def get_bar_arr(self, symbol, start_dt, end_dt, fields):
        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager:
            return curr_bar_manager.data_bar[(curr_bar_manager.index >= start_dt) & (curr_bar_manager.index <= end_dt)][fields]
        else:
            return None


minute_bar_util = BarUtil()
daily_bar_util = BarUtil()


class Data(object):
    def __init__(self, dt):
        self.dt = dt

    @staticmethod
    def current(assets, fields):
        if type(assets) == list:
            if type(fields) == list:
                return pd.DataFrame([minute_bar_util.get_last_bar(asset) for asset in assets], index=assets)
            else:
                return pd.Series([minute_bar_util.get_last_bar(asset, fields) for asset in assets], index=assets)
        else:
            return minute_bar_util.get_last_bar(symbol=assets, fields=fields)

    def history(self, assets, fields, bar_count, frequency='1m'):
        start_dt = self.dt - bar_count * timedelta(minutes=bar_count)
        end_dt = self.dt

        if frequency == '1m':
            if type(assets) == list:
                if type(fields) == list:
                    ret = {}
                    for asset in assets:
                        ret[asset] = minute_bar_util.get_bar_arr(asset, start_dt, end_dt, fields)
                    return pd.Panel(ret)
                else:
                    return pd.DataFrame([minute_bar_util.get_bar_arr(asset, start_dt, end_dt, fields) for asset in assets], columns=assets)
            else:
                return minute_bar_util.get_bar_arr(assets, start_dt, end_dt, fields)
        return None
