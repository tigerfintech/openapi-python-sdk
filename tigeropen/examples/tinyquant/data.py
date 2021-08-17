import pytz
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from tigeropen.common.consts import BarPeriod
from .client import quote_client
from .setting import MARKET

COLUMNS = ['symbol', 'time', 'open', 'high', 'low', 'close', 'volume']


class BarManager:
    def __init__(self):
        self.curr_bar = None
        self.data_bar = pd.DataFrame(columns=COLUMNS)
        self.last_minute = None
        self.last_volume = 0.0
        self.last_timestamp = None


class BarUtil:
    def __init__(self):
        self.bar_manager = {}
        self.timezone = pytz.timezone(MARKET.TIMEZONE)

        if MARKET.LUNCH_BREAK_START_TIME:
            today = datetime.now(tz=self.timezone).date()
            self.lunch_break_start = datetime.combine(today, datetime.strptime(MARKET.LUNCH_BREAK_START_TIME, '%H:%M:%S').time()).astimezone(self.timezone)
            self.lunch_break_end = datetime.combine(today, datetime.strptime(MARKET.LUNCH_BREAK_END_TIME, '%H:%M:%S').time()).astimezone(self.timezone)
        else:
            self.lunch_break_start = None
            self.lunch_break_end = None

        if MARKET.name == 'CN' or MARKET.name == 'SH' or MARKET.name == 'SZ':
            self.bar_func = self.get_bar_arr
        else:
            self.bar_func = quote_client.get_bars

    def on_data(self, symbol, items):
        """
        1.according to the market data time, market ticker data is splitted into minute bar
        2.the last bar is stored into data_bar after the current minute changes to the next minute.
          e.g. 9:30:59 -> 9:31:01
        3.user could change the split method to get the latest minute to shorten the delay.
          e.g. change when second reaches to 55, 9:30:54 -> 9:30:56
        """
        price_dict = dict(items)
        latest_price = price_dict.get('latest_price')
        volume = price_dict.get('volume')
        timestamp = price_dict.get('latest_time')

        curr_datetime_minute = (pd.to_datetime(timestamp, unit='ms').tz_localize('utc').tz_convert(MARKET.TIMEZONE)).replace(second=0, microsecond=0)

        if self.lunch_break_start and self.lunch_break_start < curr_datetime_minute < self.lunch_break_end:
            return

        curr_bar_manager = self.bar_manager.get(symbol)
        if latest_price:
            if curr_bar_manager:
                start_idx = curr_bar_manager.last_minute

                if curr_datetime_minute > start_idx:
                    if (curr_datetime_minute >= self.lunch_break_end) and (start_idx <= self.lunch_break_start):
                        delta1 = self.lunch_break_start - start_idx
                        delta2 = curr_datetime_minute - self.lunch_break_end

                        for i in range(delta1.seconds // 60):
                            curr_bar = curr_bar_manager.curr_bar.copy()
                            idx_datetime = start_idx + timedelta(minutes=i)
                            curr_bar.time = int(idx_datetime.timestamp() * 1000)
                            curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar, ignore_index=True)

                        for i in range(delta2.seconds // 60):
                            curr_bar = curr_bar_manager.curr_bar.copy()
                            idx_datetime = self.lunch_break_end + timedelta(minutes=i)
                            curr_bar.time = int(idx_datetime.timestamp() * 1000)
                            curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar, ignore_index=True)
                    else:
                        delta = curr_datetime_minute - start_idx
                        for i in range(delta.seconds // 60):
                            curr_bar = curr_bar_manager.curr_bar.copy()
                            idx_datetime = start_idx + timedelta(minutes=i)
                            curr_bar.time = int(idx_datetime.timestamp() * 1000)

                            curr_bar_manager.data_bar = curr_bar_manager.data_bar.append(curr_bar, ignore_index=True)

                    curr_bar_manager.last_timestamp = timestamp

                    # update latest
                    curr_bar_manager.curr_bar = pd.Series([symbol, int(curr_datetime_minute.timestamp() * 1000),
                                                           latest_price, latest_price, latest_price,
                                                           latest_price, volume - curr_bar_manager.last_volume], index=COLUMNS)
                    curr_bar_manager.last_minute = curr_datetime_minute
                    curr_bar_manager.last_volume = volume
                elif curr_datetime_minute == start_idx:
                    if timestamp > curr_bar_manager.last_timestamp:
                        curr_bar_manager.curr_bar.high = max(curr_bar_manager.curr_bar.high, latest_price)
                        curr_bar_manager.curr_bar.low = min(curr_bar_manager.curr_bar.low, latest_price)
                        curr_bar_manager.curr_bar.close = latest_price
                        curr_bar_manager.curr_bar.volume = volume - curr_bar_manager.last_volume
                        curr_bar_manager.last_timestamp = timestamp
            else:
                curr_bar_manager = BarManager()
                self.bar_manager[symbol] = curr_bar_manager
                curr_bar_manager.curr_bar = pd.Series([symbol, int(curr_datetime_minute.timestamp() * 1000),
                                                       latest_price, latest_price, latest_price,
                                                       latest_price, volume], index=COLUMNS)
                curr_bar_manager.last_minute = curr_datetime_minute
                curr_bar_manager.last_volume = volume
                curr_bar_manager.last_timestamp = timestamp

    def get_bar_arr(self, symbols, period, limit, end_time):
        if period == BarPeriod.DAY:
            return quote_client.get_bars(symbols=symbols, period=period, limit=limit, end_time=end_time)
        else:
            frames = []
            for symbol in symbols:
                curr_bar_manager = self.bar_manager.get(symbol)
                if curr_bar_manager:
                    df = curr_bar_manager.data_bar
                    curr_df = df[(df['time'] < end_time)].tail(limit)
                    frames.append(curr_df)
                else:
                    frames.append(pd.DataFrame(columns=COLUMNS))

            return pd.concat(frames)

    def get_bars(self, symbols, period, limit, end_time):
        return self.bar_func(symbols=symbols, period=period, limit=limit, end_time=end_time)


minute_bar_util = BarUtil()


class StockQuote:
    def __init__(self, time):
        self.time = time

    @staticmethod
    def get_bars(symbol, period, limit, end_ts):
        return minute_bar_util.get_bars(symbols=[symbol], period=period, limit=limit, end_time=end_ts)

    def current(self, assets, fields):

        if isinstance(assets, list):
            symbols = assets
        else:
            symbols = [assets]

        end_ts = int(self.time.timestamp() * 1000)
        bars = list()
        for symbol in symbols:
            bar = self.get_bars(symbol, BarPeriod.ONE_MINUTE, 1, end_ts)
            bars.append(bar)
        data = pd.concat(bars, ignore_index=True)
        if data.empty:
            return np.nan
        if isinstance(assets, list) and isinstance(fields, list):
            return data[fields].set_index(pd.Series(assets))
        elif isinstance(assets, list):
            return data.set_index(pd.Series(assets))[fields]
        elif isinstance(fields, list):
            return data[fields].transpose()[0]
        else:
            return data[fields].iloc[0]

    def history(self, assets, fields, bar_count, frequency='1m'):
        if frequency == '1m':
            period = BarPeriod.ONE_MINUTE
        else:
            period = BarPeriod.DAY
        end_dt = self.time
        end_ts = int(end_dt.timestamp() * 1000)

        if isinstance(assets, list):
            symbols = assets
        else:
            symbols = [assets]

        bars = list()
        for symbol in symbols:
            bar = self.get_bars(symbol, period, bar_count, end_ts)
            bars.append(bar)
        data = pd.concat(bars, ignore_index=True)
        if data.empty:
            return np.nan
        data.time = pd.to_datetime(data.time, unit='ms').dt.tz_localize('utc').dt.tz_convert(MARKET.TIMEZONE)
        if isinstance(assets, list) and isinstance(fields, list):
            return data.set_index(['time', 'symbol']).to_panel()[fields]
        elif isinstance(assets, list):
            result = data.pivot(index='time', columns='symbol')[fields]
            result.index.name = None
            result.columns.name = None
            return result
        elif isinstance(fields, list):
            result = data.set_index('time')[fields]
            result.index.name = None
            return result
        else:
            result = data.set_index('time')[fields]
            result.index.name = None
            return result
