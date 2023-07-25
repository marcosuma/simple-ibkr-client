import collections
import math
import statistics
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from scipy.signal import argrelextrema
import plotly.graph_objects as go
from sklearn.cluster import KMeans

colors = [
    "#fff100",
    "#ff8c00",
    "#e81123",
    "#ec008c",
    "#68217a",
    "#00188f",
    "#00bcf2",
    "#00b294",
    "#009e49",
    "#bad80a",
]


class SupportResistanceV1(object):
    def __init__(self, plotsQueue, fileToSave):
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def execute(self, df):
        df = self.__fn_impl(df)
        # df.to_csv(self.fileToSave)
        return df

    def __cluster_values(self, values):
        K = 6
        kmeans = KMeans(n_clusters=K, n_init=K).fit(values.reshape(-1, 1))

        # predict which cluster each price is in
        clusters = kmeans.predict(values.reshape(-1, 1))
        return clusters

    def __fn_impl(self, df: pd.DataFrame):
        n = 200  # number of points to be checked before and after
        df["min"] = df.iloc[
            argrelextrema(df["close"].values, np.less_equal, order=n)[0]
        ]["close"]
        df["max"] = df.iloc[
            argrelextrema(df["close"].values, np.greater_equal, order=n)[0]
        ]["close"]

        min_values = df["min"]
        max_values = df["max"]
        min_values.dropna(inplace=True)
        max_values.dropna(inplace=True)
        min_max = min_values.combine(
            max_values, lambda x, y: x if not math.isnan(x) else y
        )

        clusters = self.__cluster_values(np.array(min_max))
        min_max_values = pd.DataFrame({"values": min_max})
        min_max_values["cluster"] = clusters.tolist()
        min_max_values["color"] = min_max_values.apply(
            lambda row: colors[int(row.cluster)], axis=1
        )

        values_by_cluster = collections.defaultdict(lambda: [])
        for i, cluster in enumerate(clusters):
            values_by_cluster[cluster].append(min_max.tolist()[i])

        avgs = []
        for cluster in values_by_cluster:
            values = values_by_cluster[cluster]
            avgs.append(statistics.mean(values))

        def printStrategyMarkersFn(fig):
            for avg in avgs:
                fig.add_hline(y=avg)

        return printStrategyMarkersFn
