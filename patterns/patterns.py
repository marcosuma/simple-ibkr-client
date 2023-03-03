import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import collections
import os
from scipy.signal import argrelextrema
from statsmodels.nonparametric.kernel_regression import KernelReg
import talib as ta
import plotly.graph_objects as go


class Patterns:
    def __init__(self, candlestickData, plotsQueue, fileToSave):
        self.candlestickData = candlestickData
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def process_data_with_file(self, df):
        print("Data loaded from file")
        self.__fn_impl(df)

    # Uses LSTM (Long Short Term Memory) to predict the closing price of an asset
    # Uses past 60 days
    def process_data(self, reqId: int, start: str, end: str):
        df = pd.DataFrame(data=np.array(self.candlestickData), columns=[
            "date", "open", "close", "high", "low", "volume"])
        df.to_csv(self.fileToSave)
        print(df)

        self.__fn_impl(df)

    def __fn_impl(self, stock_df: pd.DataFrame):
        # stock_df = pd.DataFrame(data=np.array(self.candlestickData), columns=[
        #     "Date", "Open", "Close", "High", "Low"])
        # self.__printCandlestick(stock_df)
        # self.__marubozuCandles(stock_df)

        local_max = argrelextrema(stock_df['high'].values, np.greater)[0]
        local_min = argrelextrema(stock_df['low'].values, np.less)[0]
        highs = stock_df.iloc[local_max, :]
        lows = stock_df.iloc[local_min, :]

        kr = KernelReg(pd.to_numeric(
            stock_df['close']), stock_df.index, var_type='c', bw=[0.85])

        smooth_prices, smoothed_local_max, smoothed_local_min, fit_fn = self.__non_param_kernel_regression(
            kr, stock_df)

        local_max_min = np.sort(np.concatenate(
            [smoothed_local_max, smoothed_local_min]))
        smooth_extrema = smooth_prices.loc[local_max_min]
        price_local_max_dt = []
        for i in smoothed_local_max:
            if (i > 1) and (i < len(stock_df['close'])-1):
                price_local_max_dt.append(pd.to_numeric(
                    stock_df['close']).iloc[i-2:i+2].idxmax())

        price_local_min_dt = []
        for i in smoothed_local_min:
            if (i > 1) and (i < len(stock_df['close'])-1):
                price_local_min_dt.append(pd.to_numeric(
                    stock_df['close']).iloc[i-2:i+2].idxmin())

        max_min = pd.concat([pd.to_numeric(stock_df.loc[price_local_min_dt, 'close']),
                            pd.to_numeric(stock_df.loc[price_local_max_dt, 'close'])]).sort_index()

        patterns = self.__find_patterns(max_min)
        # print(patterns)
        for name, pattern_periods in patterns.items():
            print(f"{name}: {len(pattern_periods)} occurences")

        def plot_window(prices, extrema, smooth_prices, smooth_extrema, ax=None):
            if ax is None:
                fig = plt.figure()
                ax = fig.add_subplot(111)

            prices.plot(ax=ax, color='dodgerblue')
            ax.scatter(extrema.index, extrema.values, color='red')
            smooth_prices.plot(ax=ax, color='lightgrey')
            ax.scatter(smooth_extrema.index,
                       smooth_extrema.values, color='lightgrey')

        def plotFn2():
            for name, pattern_periods in patterns.items():
                if name == 'HS':
                    print(name)

                    rows = int(np.ceil(len(pattern_periods)/2))
                    f, axes = plt.subplots(rows, 2, figsize=(20, 5*rows))
                    axes = axes.flatten()
                    i = 0
                    for start, end in pattern_periods:
                        s = stock_df.index[start-1]
                        e = stock_df.index[end+1]

                        plot_window(pd.to_numeric(stock_df['close'])[s:e], max_min.loc[s:e],
                                    smooth_prices[s:e],
                                    smooth_extrema.loc[s:e], ax=axes[i])
                        i += 1
                    plt.show()

        def plotFn():
            fig, axs = plt.subplots(2)
            fig.suptitle("Plots")

            pd.to_numeric(stock_df['low']).plot(ax=axs[0])
            pd.to_numeric(stock_df['high']).plot(ax=axs[0])
            axs[0].scatter(highs.index, pd.to_numeric(highs["high"]))
            axs[0].scatter(lows.index, pd.to_numeric(lows["low"]))

            # axs[1].plot(pd.to_numeric(stock_df['Close']))
            # axs[1].plot(pd.to_numeric(stock_df['Close']).rolling(window=5).mean())

            # stock_df['Close'].rolling(window=4).mean().plot(
            #     ax=axs[1], legend="Stock close")
            # smooth_prices = pd.Series(data=f[0], index=stock_df.index)
            # # smooth_prices_2 = pd.Series(data=f2[0], index=stock_df.index)
            # smooth_prices.plot(ax=axs[1])
            # # smooth_prices_2.plot(ax=axs[1])

            pd.to_numeric(stock_df['close']).plot(
                ax=axs[1], legend=True, color='dodgerblue')
            axs[1].scatter(max_min.index, max_min.values, color='red')
            pd.to_numeric(smooth_prices).plot(
                ax=axs[1], legend=True, color='lightgray')
            axs[1].scatter(smooth_extrema.index,
                           smooth_extrema.values, color='red')

            plt.grid(True)
            plt.show()

        self.plotsQueue.append(plotFn2)

    def __non_param_kernel_regression(self, kr, stock_df):
        f = kr.fit([stock_df.index.values])
        smooth_prices = pd.Series(data=f[0], index=stock_df.index)
        smoothed_local_max = argrelextrema(smooth_prices.values, np.greater)[0]
        smoothed_local_min = argrelextrema(smooth_prices.values, np.less)[0]
        # print(smoothed_local_max)
        # print(local_max)
        return smooth_prices, smoothed_local_max, smoothed_local_min, f

    def __find_patterns(self, extrema, max_bars=35):
        """
        Input:
            s: extrema as pd.series with bar number as index
            max_bars: max bars for pattern to play out
        Returns:
            patterns: patterns as a defaultdict list of tuples
            containing the start and end bar of the pattern
        """
        patterns = collections.defaultdict(list)

        # Need to start at five extrema for pattern generation
        for i in range(5, len(extrema)):
            window = extrema.iloc[i-5:i]

            # A pattern must play out within max_bars (default 35)
            if (window.index[-1] - window.index[0]) > max_bars:
                continue

            # Using the notation from the paper to avoid mistakes
            e1 = window.iloc[0]
            e2 = window.iloc[1]
            e3 = window.iloc[2]
            e4 = window.iloc[3]
            e5 = window.iloc[4]

            rtop_g1 = np.mean([e1, e3, e5])
            rtop_g2 = np.mean([e2, e4])
            # Head and Shoulders
            if (e1 > e2) and (e3 > e1) and (e3 > e5) and \
                (abs(e1 - e5) <= 0.03*np.mean([e1, e5])) and \
                    (abs(e2 - e4) <= 0.03*np.mean([e1, e5])):
                patterns['HS'].append((window.index[0], window.index[-1]))

            # Inverse Head and Shoulders
            elif (e1 < e2) and (e3 < e1) and (e3 < e5) and \
                (abs(e1 - e5) <= 0.03*np.mean([e1, e5])) and \
                    (abs(e2 - e4) <= 0.03*np.mean([e1, e5])):
                patterns['IHS'].append((window.index[0], window.index[-1]))

            # Broadening Top
            elif (e1 > e2) and (e1 < e3) and (e3 < e5) and (e2 > e4):
                patterns['BTOP'].append((window.index[0], window.index[-1]))

            # Broadening Bottom
            elif (e1 < e2) and (e1 > e3) and (e3 > e5) and (e2 < e4):
                patterns['BBOT'].append((window.index[0], window.index[-1]))

            # Triangle Top
            elif (e1 > e2) and (e1 > e3) and (e3 > e5) and (e2 < e4):
                patterns['TTOP'].append((window.index[0], window.index[-1]))

            # Triangle Bottom
            elif (e1 < e2) and (e1 < e3) and (e3 < e5) and (e2 > e4):
                patterns['TBOT'].append((window.index[0], window.index[-1]))

            # Rectangle Top
            elif (e1 > e2) and (abs(e1-rtop_g1)/rtop_g1 < 0.0075) and \
                (abs(e3-rtop_g1)/rtop_g1 < 0.0075) and (abs(e5-rtop_g1)/rtop_g1 < 0.0075) and \
                (abs(e2-rtop_g2)/rtop_g2 < 0.0075) and (abs(e4-rtop_g2)/rtop_g2 < 0.0075) and \
                    (min(e1, e3, e5) > max(e2, e4)):

                patterns['RTOP'].append((window.index[0], window.index[-1]))

            # Rectangle Bottom
            elif (e1 < e2) and (abs(e1-rtop_g1)/rtop_g1 < 0.0075) and \
                (abs(e3-rtop_g1)/rtop_g1 < 0.0075) and (abs(e5-rtop_g1)/rtop_g1 < 0.0075) and \
                (abs(e2-rtop_g2)/rtop_g2 < 0.0075) and (abs(e4-rtop_g2)/rtop_g2 < 0.0075) and \
                    (max(e1, e3, e5) > min(e2, e4)):
                patterns['RBOT'].append((window.index[0], window.index[-1]))

        return patterns

    def __printCandlestick(self, stock_df):
        candlestick = go.Candlestick(x=stock_df["Date"],
                                     open=stock_df["Open"],
                                     high=stock_df["High"],
                                     low=stock_df["Low"],
                                     close=stock_df["Close"])
        fig = go.Figure(data=[candlestick])
        fig.layout.xaxis.type = 'category'
        fig.show()

    def __marubozuCandles(self, stock_df):
        # Identify the marubozu candles in the dataset
        stock_df['marubozu'] = ta.CDLMARUBOZU(
            stock_df['Open'], stock_df['High'], stock_df['Low'], stock_df['Close'])
        # Subset dataframe for only the marubozu candles
        marubozu_candles = stock_df[stock_df['marubozu'] != 0]

        # display(marubozu_candles[['Close', 'marubozu']])
        self.__printCandlestick(marubozu_candles)
