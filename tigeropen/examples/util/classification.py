import os
import pytz
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from tslearn.clustering import TimeSeriesKMeans


def check_file_exists(file_path):
    return os.path.isfile(file_path)


def dtw_distance(s1, s2):
    dtw = {}

    for i in range(len(s1)):
        dtw[(i, -1)] = float('inf')
    for i in range(len(s2)):
        dtw[(-1, i)] = float('inf')

    dtw[(-1, -1)] = 0
    for i in range(len(s1)):
        for j in range(len(s2)):
            dist = (s1[i] - s2[j])**2
            dtw[(i, j)] = dist + min(dtw[(i-1, j)], dtw[i, j-1], dtw[i-1, j-1])

    return sqrt(dtw[len(s1)-1, len(s2)-1])


class Classification:
    def __init__(self, today):
        self.today = today.strftime('%Y-%m-%d')
        self.dir_path = f'./data/{self.today}'
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

    def classify(self):
        # ========================================================
        print('Euclidean k-means')
        df = pd.DataFrame(self.daily_return).iloc[1: -2, :].T.dropna(how='any')
        km = TimeSeriesKMeans(n_clusters=10, verbose=True, random_state=0)
        y_pred = km.fit_predict(df.values)
        results = pd.DataFrame(df.index, y_pred)

        plt.figure()
        for yi in range(10):
            # plt.subplot(10, 10, yi + 1)
            curr_df = results[results.index == yi]
            for row in curr_df.iterrows():
                symbol = row[1][0]
                plt.plot(df[df.index == symbol].values[0], 'k-', alpha=.2)
            plt.plot(km.cluster_centers_[yi], 'r-')

            plt.xlim(0, df.shape[1])
            plt.show()
            plt.cla()

        # ========================================================
        print('DBA k-means')
        df = pd.DataFrame(self.daily_return).iloc[1: -2, :].T.dropna(how='any')
        km = TimeSeriesKMeans(n_clusters=10, n_init=2, metric="dtw", verbose=True,  max_iter_barycenter=10)
        y_pred = km.fit_predict(df.values)
        results = pd.DataFrame(df.index, y_pred)

        plt.figure()
        for yi in range(10):
            # plt.subplot(10, 10, yi + 1)
            curr_df = results[results.index == yi]
            for row in curr_df.iterrows():
                symbol = row[1][0]
                plt.plot(df[df.index == symbol].values[0], 'k-', alpha=.2)
            plt.plot(km.cluster_centers_[yi], 'r-')

            plt.xlim(0, df.shape[1])
            plt.show()
            plt.cla()


if __name__ == '__main__':
    classification = Classification(datetime.today().date() - timedelta(days=1))
    classification.classify()

