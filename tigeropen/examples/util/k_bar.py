import os
import pytz
import numpy as np
import pandas as pd
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.dates as mdates
import scipy.stats as stats
from mpl_finance import candlestick_ohlc

from tigeropen.common.consts import Market


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
    def __init__(self):
        self.today = datetime.today().date().strftime('%Y-%m-%d')
        self.dir_path = f'./data/{self.today}'
        check_and_create_dir(self.dir_path)
        self.market_timezone = pytz.timezone('America/New_York')
        self.timezone = pytz.timezone('Asia/Shanghai')
        self.daily_return_path = f'{self.dir_path}/ret.pkl'

        if check_file_exists(self.daily_return_path):
            self.daily_return = pd.read_pickle(self.daily_return_path).to_dict('series')
        else:
            self.daily_return = {}

        self.daily_stats_path = f'{self.dir_path}/stats'

    def plot(self, symbol_str, df, freq=3):
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

        ret_list = []
        for key, value in self.daily_return.items():
            if value.size <= 0:
                print(key)
                continue
            if np.isnan(value.iloc[-1]):
                print(key)
                continue
            ret_list.append(value.iloc[-1])

        # ret_list = [value.iloc[-1] for value in self.daily_return.values()]
        avg_return = np.mean(ret_list)
        median_return = np.median(ret_list)
        std_return = np.std(ret_list)
        skew_return = stats.skew(np.array(ret_list))
        kurt_return = stats.kurtosis(ret_list)
        size = len(ret_list)

        count_1_std = np.sum(np.array(ret_list) > (avg_return + std_return * 1.0))
        ratio_1 = count_1_std / size

        count_2_std = np.sum(np.array(ret_list) > (avg_return + std_return * 2.0))
        ratio_2 = count_2_std / size

        count_3_std = np.sum(np.array(ret_list) > (avg_return + std_return * 3.0))
        ratio_3 = count_3_std / size

        x = np.linspace(avg_return - 3 * std_return, avg_return + 3 * std_return, 100)
        y = mlab.normpdf(x, avg_return, std_return)

        kde = stats.gaussian_kde(ret_list)

        plt.subplot(121)
        plt.hist(ret_list, bins=100)

        plt.axvline(x=avg_return, color='red', linestyle='--', linewidth=0.8, label='mean')
        plt.axvline(x=avg_return - 2 * std_return, color='blue', linestyle='--', linewidth=0.8,
                    label='-2 std deviation')
        plt.axvline(x=avg_return + 2 * std_return, color='blue', linestyle='--', linewidth=0.8, label='2 std deviation')
        plt.axvline(x=avg_return - 3 * std_return, color='orange', linestyle='--', linewidth=0.8,
                    label='-3 std deviation')
        plt.axvline(x=avg_return + 3 * std_return, color='orange', linestyle='--', linewidth=0.8,
                    label='3 std deviation')
        plt.ylabel('percentage', fontsize=10)
        plt.legend(fontsize=12)

        plt.subplot(122)
        plt.plot(x, kde(x), label='kernel density estimation')
        plt.plot(x, y, color='black', linewidth=1, label='normal fit')
        plt.ylabel('probability', fontsize=10)
        plt.axvline(x=avg_return, color='red', linestyle='--', linewidth=0.8, label='mean')
        plt.axvline(x=avg_return - 2 * std_return, color='blue', linestyle='--', linewidth=0.8,
                    label='-2 std deviation')
        plt.axvline(x=avg_return + 2 * std_return, color='blue', linestyle='--', linewidth=0.8, label='2 std deviation')
        plt.axvline(x=avg_return - 3 * std_return, color='orange', linestyle='--', linewidth=0.8,
                    label='-3 std deviation')
        plt.axvline(x=avg_return + 3 * std_return, color='orange', linestyle='--', linewidth=0.8,
                    label='3 std deviation')
        plt.legend(fontsize=12, loc='best')
        plt.show()
        plt.savefig(f'{self.dir_path}/sum.png')
        plt.cla()

        dump_dict = {'avg_return:': avg_return, 'median_return': median_return, 'std_return': std_return,
                     'skew_return': skew_return, 'kurt_return': kurt_return, 'size': size,
                     'above_1_std_ratio': ratio_1, 'above_2_std_ratio': ratio_2, 'above_3_std_ratio': ratio_3}

        store_dict(dump_dict, self.daily_stats_path)


k_bar_util = KBarUtil()


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

    try:
        for symbol_str in stk_arr:
            print(f'total stk_size: {stk_size}, {idx}')
            bars = quote_client.get_bars([symbol_str], limit=30)
            k_bar_util.plot(symbol_str, bars)
            idx += 1
    except Exception as e:
        print(e)

    k_bar_util.dump()

    # symbol = '600030'
    # bars = quote_client.get_bars([symbol], limit=30)
    # print(bars)
    # k_bar_util.plot(symbol, bars)


