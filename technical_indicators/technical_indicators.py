import numpy as np
import pandas as pd


class TechnicalIndicators(object):
    def __init__(self, candlestickData, plotsQueue, fileToSave):
        self.candlestickData = candlestickData
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def process_data_with_file(self, df):
        print("Data loaded from file")
        self.__fn_impl(df)
        df.to_csv(self.fileToSave)
        return df

    # Uses LSTM (Long Short Term Memory) to predict the closing price of an asset
    # Uses past 60 days
    def process_data(self, reqId: int, start: str, end: str):
        df = pd.DataFrame(data=np.array(self.candlestickData), columns=[
            "date", "open", "close", "high", "low", "volume"])
        df["date"] = df["date"].astype(int)
        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)

        self.__fn_impl(df)
        df.to_csv(self.fileToSave)
        return df

    def __fn_impl(self, df: pd.DataFrame):
        df['shifted_open'] = df.open.shift(-1)

        from technical_indicators.sma.sma import SMA
        from technical_indicators.ema.ema import EMA
        from technical_indicators.rsi.rsi import RSI
        from technical_indicators.macd.macd import MACD
        from technical_indicators.adx.adx import ADX
        from technical_indicators.bollinger_bands.bollinger_bands import BollingerBands
        SMA().calculate(df)
        EMA().calculate(df)
        RSI().calculate(df)
        MACD().calculate(df)
        ADX().calculate(df)
        BollingerBands().calculate(df)

        from stockstats import wrap
        ss_df = wrap(df)


"""
# View our data
        pd.set_option("display.max_columns", None)
        print(df)

        def plotFn():
            # Construct a 2 x 1 Plotly figure
            fig = make_subplots(rows=2, cols=1)
            # price Line
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['open'],
                    line=dict(color='#ff9900', width=1),
                    name='open',
                    # showlegend=False,
                    legendgroup='1',
                ), row=1, col=1
            )
            # Candlestick chart for pricing
            fig.append_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    increasing_line_color='#ff9900',
                    decreasing_line_color='black',
                    showlegend=False
                ), row=1, col=1
            )
            




            # Make it pretty
            layout = go.Layout(
                plot_bgcolor='#efefef',
                # Font Families
                font_family='Monospace',
                font_color='#000000',
                font_size=20,
                xaxis=dict(
                    rangeslider=dict(
                        visible=False
                    )
                )
            )
            # Update options and show plot
            fig.update_layout(layout)
            fig.show()

        self.plotsQueue.append(plotFn)
"""
