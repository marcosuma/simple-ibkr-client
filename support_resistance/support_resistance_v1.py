import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from scipy.signal import argrelextrema
import plotly.graph_objects as go
from sklearn.cluster import KMeans


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
        K = 10
        kmeans = KMeans(n_clusters=K).fit(values.reshape(-1, 1))

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

        # _df = df.copy()
        # _df.dropna(inplace=True)
        # print("min values", df["min"])
        # print(df["min"].describe())
        min_values = df["min"]
        max_values = df["max"]
        min_values.dropna(inplace=True)
        max_values.dropna(inplace=True)
        min_values = np.array(min_values)
        max_values = np.array(max_values)

        min_clusters = self.__cluster_values(min_values)
        max_clusters = self.__cluster_values(max_values)

        print(min_clusters)
        print(max_clusters)

        def printStrategyMarkersFn(fig):
            pass
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df["min"] - 0.01,
                    name="Buy Action",
                    # showlegend=False,
                    legendgroup="2",
                    mode="markers",
                    marker=dict(
                        color="blue",
                        line=dict(color="blue", width=2),
                        symbol="triangle-down",
                    ),
                ),
                row=1,
                col=1,
            )
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df["max"] + 0.01,
                    name="Sell Action",
                    # showlegend=False,
                    legendgroup="2",
                    mode="markers",
                    marker=dict(
                        color="blue",
                        line=dict(color="blue", width=2),
                        symbol="triangle-up",
                    ),
                ),
                row=1,
                col=1,
            )

        # def plotFn():
        #     plt.scatter(df.index, df['min'], c='r')
        #     plt.scatter(df.index, df['max'], c='g')
        #     plt.plot(df.index, df['close'])
        #     plt.show()

        # self.plotsQueue.append(plotFn)

        return printStrategyMarkersFn
