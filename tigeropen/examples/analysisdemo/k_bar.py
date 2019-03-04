import os
import pytz
import numpy as np
import pandas as pd
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
import scipy.stats as stats
from mpl_finance import candlestick_ohlc

from sklearn.cluster import  KMeans
from tigeropen.common.consts import Market
from math import sqrt
from tslearn.clustering import TimeSeriesKMeans


def store_dict(dump_dict, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(dump_dict, f, protocol=2)


def load_dict(file_path):
    with open(file_path, 'rb') as f:
        ret = pickle.load(file_path)
        return ret


def check_and_create_dir(dir_path):
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def check_file_exists(file_path):
    return os.path.isfile(file_path)


class KBarUtil:
    def __init__(self, today):
        self.today = today.strftime('%Y-%m-%d')
        self.dir_path = f'./data/{self.today}'
        check_and_create_dir(self.dir_path)
        self.market_timezone = pytz.timezone('America/New_York')
        self.timezone = pytz.timezone('Asia/Shanghai')
        self.daily_return_path = f'{self.dir_path}/ret.pkl'

        if check_file_exists(self.daily_return_path):
            self.daily_return = pd.read_pickle(self.daily_return_path).to_dict('series')
        else:
            self.daily_return = {}

        self.daily_volume_ratio_path = f'{self.dir_path}/vol.pkl'
        if check_file_exists(self.daily_volume_ratio_path):
            self.daily_volume_ratio = pd.read_pickle(self.daily_volume_ratio_path)
        else:
            self.daily_volume_ratio = {}

        self.daily_stats_path = f'{self.dir_path}/stats'

    def plot(self, symbol_str, df, freq=3):
        """
        plot and save k bars & volume
        :param symbol_str:
        :param df: stock price data
        :param freq: x axis frequency
        :return:
        """
        if len(df) <= 0:
            return

        df['date'] = pd.to_datetime(df['time'], unit='ms')
        date_strs = []

        for date in df['date']:
            date_strs.append(date.replace(tzinfo=self.market_timezone).tz_convert(self.timezone).date().strftime('%Y-%m-%d'))

        # remove no current data
        if date_strs[-1] != self.today:
            return

        self.daily_return[symbol_str] = df['close'].diff() / df['close'].shift()
        self.daily_volume_ratio[symbol_str] = df['volume'].diff() / df['volume'].shift()

        df["date"] = df["date"].apply(mdates.date2num)

        quotes = df[['date', 'open', 'high', 'low', 'close']].copy()
        quotes.reset_index()
        quotes['date'] = quotes.index
        # quotes['sma50'] = quotes["close"].rolling(10).mean()

        fig, (ax1, ax2) = plt.subplots(nrows=2, sharex='all', figsize=(15, 8))
        fig.subplots_adjust(bottom=0.2)

        ax1.set_xticks(quotes.index[::3])
        ax1.set_xticklabels(date_strs[::3], rotation=45, ha='right')
        ax1.set_xlim(quotes.index.min(), quotes.index.max())
        ax1.set_title(f'{symbol_str}')
        ax1.set_ylabel('price')
        ax1.grid(True)
        candlestick_ohlc(ax1, quotes.values, width=0.5, colorup='red', colordown='green')

        ax1.set_xticks(quotes.index[::freq])
        ax1.set_xticklabels(date_strs[::freq], rotation=45, ha='right')
        ax1.set_xlim(quotes.index.min(), quotes.index.max())
        ax2.set_ylabel('volume')
        plt.bar(quotes.index, df['volume'], width=0.5)
        plt.savefig(f'{self.dir_path}/{symbol_str}.png')
        plt.cla()
        plt.close()

    def dump(self):
        pd.DataFrame(self.daily_return).to_pickle(self.daily_return_path)
        pd.DataFrame(self.daily_volume_ratio).to_pickle(self.daily_volume_ratio_path)


def filter_stock(symbols):
    ret = []
    for symbol_tuple in symbols:
        # exclude st and index
        if 'ST' in symbol_tuple[1] or '.SH' in symbol_tuple[0]:
            continue
        if symbol_tuple[0][0:2] == '00' or symbol_tuple[0][0:2] == '60' or symbol_tuple[0][0:2] == '30':
            ret.append(symbol_tuple[0])
    return ret


if __name__ == '__main__':
    from tigeropen.examples.client_config import get_client_config
    from tigeropen.quote.quote_client import QuoteClient

    client_config = get_client_config()
    quote_client = QuoteClient(client_config, logger=None)

    stk_list = quote_client.get_symbol_names(market=Market.CN)

    stk_arr = filter_stock(stk_list)
    stk_size = len(stk_arr)
    idx = 0

    k_bar_util = KBarUtil(datetime.today().date())
    # k_bar_util = KBarUtil(datetime.today().date() - timedelta(days=1))

    try:
        for symbol_str in stk_arr:
            print(f'total stk_size: {stk_size}, {idx}')
            bars = quote_client.get_bars([symbol_str], limit=30)
            k_bar_util.plot(symbol_str, bars)
            idx += 1
    except Exception as e:
        print(e)

    k_bar_util.dump()


