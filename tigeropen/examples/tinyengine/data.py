from datetime import datetime, timedelta
import pandas as pd
import numpy as np


COLUMNS = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']


class BarManager(object):
    def __init__(self):
        self.curr_bar = None
        self.last_bar = None
        self.data_bar = pd.DataFrame(columns=COLUMNS)
        # self.data_bar.set_index('time')
        self.last_minute = None
        self.last_volume = 0.0


class BarUtil(object):
    def __init__(self):
        self.bar_manager = {}

    def on_data(self, symbol, items):
        price_dict = dict(items)
        latest_price = price_dict.get('latest_price')
        volume = price_dict.get('volume')
        timestamp = price_dict.get('latest_time')

        curr_datetime_minute = datetime.fromtimestamp(timestamp / 1000).replace(second=0)

        curr_minute = curr_datetime_minute.minute

        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager:
            if curr_minute != curr_bar_manager.last_minute:

                # finish last bar
                curr_bar_manager.last_bar = curr_bar_manager.curr_bar.copy()

                start_idx = curr_bar_manager.last_minute
                end_idx = 60 if curr_minute == 0 else curr_minute

                # update history
                for minute_idx in range(start_idx, end_idx):
                    curr_bar = curr_bar_manager.curr_bar.copy()
                    idx_datetime = curr_datetime_minute.replace(minute=minute_idx)
                    curr_bar.name = idx_datetime
                    curr_bar.time = idx_datetime.timestamp()
                    curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar)

                # update latest
                curr_bar_manager.curr_bar = pd.Series([symbol, timestamp, latest_price, latest_price, latest_price,
                                                       latest_price, volume], index=COLUMNS)
                curr_bar_manager.last_minute = curr_minute
                curr_bar_manager.last_volume = volume
            else:
                # set time for test
                curr_bar_manager.curr_bar.time = timestamp
                curr_bar_manager.curr_bar.high = max(curr_bar_manager.curr_bar.high, latest_price)
                curr_bar_manager.curr_bar.low = min(curr_bar_manager.curr_bar.low, latest_price)
                curr_bar_manager.curr_bar.close = latest_price
                curr_bar_manager.curr_bar.volume = volume - curr_bar_manager.last_volume
        else:
            curr_bar_manager = BarManager()
            self.bar_manager[symbol] = curr_bar_manager
            curr_bar_manager.curr_bar = pd.Series([symbol, timestamp, latest_price, latest_price, latest_price,
                                                   latest_price, volume], index=COLUMNS)
            curr_bar_manager.last_bar = curr_bar_manager.curr_bar.copy()
            curr_bar_manager.last_minute = curr_minute

    # def set_data(self, data):
    #     for curr_bar_manager in self.bar_manager.values():
    #         if curr_bar_manager.last_bar:
    #             curr_bar = curr_bar_manager.last_bar.copy()
    #             curr_bar.name = data.dt
    #             curr_bar.time = data.dt.timestamp()
    #             curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar)

    def get_last_bar(self, symbol, fields):
        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager and type(curr_bar_manager.last_bar) == pd.Series:
            return curr_bar_manager.last_bar[fields]
        else:
            if type(fields) == list:
                ret_arr = np.empty(len(fields), dtype=float)
                ret_arr.fill(np.nan)
                return pd.Series(ret_arr, index=fields)
            return np.nan

    def get_bar_arr(self, symbol, start_dt, end_dt, fields):
        curr_bar_manager = self.bar_manager.get(symbol)
        if curr_bar_manager:
            # return curr_bar_manager.data_bar[(curr_bar_manager.data_bar.index >= start_dt) & (curr_bar_manager.data_bar.index <= end_dt)][fields]
            return curr_bar_manager.data_bar[(curr_bar_manager.data_bar.index >= start_dt.strftime('%Y-%m-%d %H:%M:%S'))
                                             & (curr_bar_manager.data_bar.index <= end_dt.strftime('%Y-%m-%d %H:%M:%S'))][fields]
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
                return pd.DataFrame([minute_bar_util.get_last_bar(asset, fields) for asset in assets], index=assets)
            else:
                return pd.Series([minute_bar_util.get_last_bar(asset, fields) for asset in assets], index=assets)
        else:
            return minute_bar_util.get_last_bar(symbol=assets, fields=fields)

    def history(self, assets, fields, bar_count, frequency='1m'):
        start_dt = self.dt - timedelta(minutes=bar_count)
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
