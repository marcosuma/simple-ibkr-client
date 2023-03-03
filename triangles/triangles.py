import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.graph_objects as go
from scipy.stats import linregress


class Triangles:
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

    def __fn_impl(self, df: pd.DataFrame):
        df.reset_index(drop=True, inplace=True)
        df.isna().sum()

        df['pivot'] = df.apply(
            lambda x: self.__pivotid(df, x.name, 3, 3), axis=1)
        df['pointpos'] = df.apply(lambda row: self.__pointpos(row), axis=1)

        backcandles = 100
        dfpl = df

        fig = go.Figure(data=[go.Candlestick(x=dfpl.index, open=dfpl['open'],
                        high=dfpl['high'], low=dfpl['low'], close=dfpl['close'])])

        fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers", marker=dict(
            size=4, color="MediumPurple"), name="pivot")

        candleid = backcandles
        while candleid < len(dfpl) - 1:
            try:
                slmin, intercmin, slmax, intercmax, xxmin, xxmax = self.__check_if_triangle(
                    candleid, backcandles, df)
                fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin +
                                         intercmin, mode='lines', name='min slope'))
                fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax +
                                         intercmax, mode='lines', name='max slope'))
                fig.update_layout(xaxis_rangeslider_visible=False)
                candleid += int(backcandles * 0.5)
            except ValueError as err:
                print(err)
                candleid += 1
                continue

        fig.show()

        # def plotFn():
        #     dfpl = df
        #     fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
        #                                          open=pd.to_numeric(dfpl['open']),
        #                                          close=pd.to_numeric(
        #                                              dfpl['close']),
        #                                          high=pd.to_numeric(dfpl['high']),
        #                                          low=pd.to_numeric(dfpl['low']))])

        #     fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers", marker=dict(
        #         size=5, color="MediumPurple"), name="pivot")

        #     fig.show()

        # plotsQueue.append(plotFn)

    def __pivotid(self, df1, l, n1, n2):  # n1 n2 before and after candle l
        if l-n1 < 0 or l+n2 >= len(df1):
            return 0

        pividlow = 1
        pividhigh = 1
        for i in range(l-n1, l+n2+1):
            if df1.low[l] > df1.low[i]:
                pividlow = 0
            if df1.high[l] < df1.high[i]:
                pividhigh = 0

        if pividlow and pividhigh:
            return 3
        elif pividlow:
            return 1
        elif pividhigh:
            return 2
        else:
            return 0

    def __pointpos(self, x):
        if x['pivot'] == 1:
            return float(x['low']) - 1e-5
        elif x['pivot'] == 2:
            return float(x['high']) + 1e-5
        else:
            return np.nan

    def __check_if_triangle(self, candleid, backcandles, df):
        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        for i in range(candleid - backcandles, candleid + 1):
            if df.iloc[i].pivot == 1:
                minim = np.append(minim, float(df.iloc[i].low))
                xxmin = np.append(xxmin, i)
            if df.iloc[i].pivot == 2:
                maxim = np.append(maxim, float(df.iloc[i].high))
                xxmax = np.append(xxmax, i)

        if (xxmax.size < 5 and xxmin.size < 5) or xxmax.size == 0 or xxmin.size == 0:
            raise ValueError(
                "no triangle found - ((xxmax.size < 3 and xxmin.size < 3) or xxmax.size == 0 or xxmin.size == 0)")

        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)

        # # and slmax <= -0.01:
        # if abs(rmax) >= 0.4 and abs(rmin) >= 0.4:  # and abs(slmin) <= 0.001:
        #     print(rmin, rmax, candleid)
        #     return slmin, intercmin, slmax, intercmax, xxmin, xxmax

        if (slmin >= 0 and slmax < 0) or (slmin > 0 and slmax <= 0):
            print(rmin, rmax, candleid)
            return slmin, intercmin, slmax, intercmax, xxmin, xxmax

        if candleid % 1000 == 0:
            print(candleid)

        raise ValueError("no triangle found")
