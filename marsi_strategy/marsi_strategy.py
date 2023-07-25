import numpy as np
from backtesting import Backtest

from marsi_strategy.backtesting.Backtesting import BacktestingStrategy
from tester.tester import Tester as MyBacktest

import plotly.graph_objects as go


class MARSIStrategy(object):
    def execute(self, df):
        rsi_above_70 = np.where(df["RSI_14"] >= 70, True, False)
        rsi_below_30 = np.where(df["RSI_14"] <= 30, True, False)
        hist = 7
        for i in range(hist, len(df.index) - hist):
            df.loc[i, "RSI_30_ok"] = (
                True if rsi_below_30[i - hist : i].sum() > 0 else False
            )
            df.loc[i, "RSI_70_ok"] = (
                True if rsi_above_70[i - hist : i].sum() > 0 else False
            )

        df["macd_trend"] = np.where(df["macd"] < df["macd_s"], -1, 1)
        df["macd_buy_signal"] = np.sign(df["macd_trend"]).diff().gt(0)
        df["macd_sell_signal"] = np.sign(df["macd_trend"]).diff().lt(0)

        df["execute_buy"] = np.where(
            df["macd_buy_signal"] & df["RSI_30_ok"],
            df["close"] + df["STDEV_30"],
            np.NaN,
        )
        df["execute_sell"] = np.where(
            df["macd_sell_signal"] & df["RSI_70_ok"],
            df["close"] - df["STDEV_30"],
            np.NaN,
        )

        cash = 5_000

        def buy_pred_fn(row):
            return row.execute_buy != np.NaN

        def sell_pred_fn(row):
            return row.execute_sell != np.NaN

        MyBacktest().test(df, cash, buy_pred_fn, sell_pred_fn)

        df["Open"] = df.open
        df["Close"] = df.close
        df["High"] = df.high
        df["Low"] = df.low
        bt = Backtest(
            df, BacktestingStrategy, cash=cash, commission=0.0002, exclusive_orders=True
        )
        stat = bt.run()
        print(stat)

        def printStrategyMarkersFn(fig):
            pass
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df["execute_buy"],
                    name="Buy Action",
                    # showlegend=False,
                    legendgroup="2",
                    mode="markers",
                    marker=dict(
                        color="green",
                        line=dict(color="green", width=2),
                        symbol="triangle-down",
                    ),
                ),
                row=1,
                col=1,
            )
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df["execute_sell"],
                    name="Sell Action",
                    # showlegend=False,
                    legendgroup="2",
                    mode="markers",
                    marker=dict(
                        color="red",
                        line=dict(color="red", width=2),
                        symbol="triangle-up",
                    ),
                ),
                row=1,
                col=1,
            )

        return printStrategyMarkersFn
