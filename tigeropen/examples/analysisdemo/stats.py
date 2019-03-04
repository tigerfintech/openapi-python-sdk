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


class StatsUtil:
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

    def analysis_var(self, ret_list, var_name):
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

        plt.title(var_name)
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
        plt.savefig(f'{self.dir_path}/{var_name}.png')
        plt.show()
        plt.cla()

        # dump stats
        # dump_dict = {'avg_return:': avg_return, 'median_return': median_return, 'std_return': std_return,
        #              'skew_return': skew_return, 'kurt_return': kurt_return, 'size': size,
        #              'above_1_std_ratio': ratio_1, 'above_2_std_ratio': ratio_2, 'above_3_std_ratio': ratio_3}
        #
        # store_dict(dump_dict, self.daily_stats_path)

    def analysis(self):
        # ========================================================
        # returns analysis
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
        self.analysis_var(ret_list, 'ret')

        # ========================================================

        # std analysis
        std_list = []
        for key, value in self.daily_return.items():
            if value.size <= 0:
                print(key)
                continue
            std = np.std(value.dropna())
            if np.isnan(std):
                print(key)
                continue
            std_list.append(std)
        self.analysis_var(std_list, 'ret_std')

        # ========================================================

        # filter stock
        stock_list = []
        for key, value in self.daily_return.items():
            if value.size <= 0:
                print(key)
                continue
            if np.isnan(value.iloc[-1]):
                print(key)
                continue
            if value.iloc[-1] > 0.02:
                stock_list.append(key)
        print(stock_list)

        # ========================================================


if __name__ == '__main__':

    stats_util = StatsUtil(datetime.today().date() - timedelta(days=1))

    stats_util.analysis()



