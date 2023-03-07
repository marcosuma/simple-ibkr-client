import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class TechnicalIndicators(object):
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
        df["close"] = df["close"].astype(float)
        print(df)

        self.__fn_impl(df)
        df.to_csv(self.fileToSave)

    def __fn_impl(self, df: pd.DataFrame):
        from technical_indicators.ema.ema import EMA
        from technical_indicators.rsi.rsi import RSI
        from technical_indicators.macd.macd import MACD
        from technical_indicators.bollinger_bands.bollinger_bands import BollingerBands
        EMA().calculate(df)
        RSI().calculate(df)
        MACD().calculate(df)
        BollingerBands().calculate(df)

        df['execute_buy'] = np.where(
            df['macd_buy_signal'] & df['RSI_30_ok'], df['close'] + 0.05, "NaN")
        df['execute_sell'] = np.where(
            df['macd_sell_signal'] & df['RSI_70_ok'], df['close'] - 0.05, "NaN")

        def plotFn():
            # Construct a 2 x 1 Plotly figure
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True)
            # price Line
            # Candlestick chart for pricing
            fig.append_trace(
                go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    increasing_line_color='green',
                    decreasing_line_color='red',
                    showlegend=False
                ), row=1, col=1
            )
            # EMA 10
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['EMA_10'],
                    line=dict(color='black', width=2),
                    name='EMA 10',
                    # showlegend=False,
                    legendgroup='2',
                ), row=1, col=1
            )
            # Bollinger up
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bollinger_up'],
                    line=dict(color='blue', width=2),
                    name='BB_up',
                    # showlegend=False,
                    legendgroup='2',
                ), row=1, col=1
            )
            # Bollinger down
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['bollinger_down'],
                    line=dict(color='blue', width=2),
                    name='BB_down',
                    # showlegend=False,
                    legendgroup='2',
                ), row=1, col=1
            )

            # Make RSI Plot
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['RSI_14'],
                line=dict(color='#ff9900', width=2),
                showlegend=False), row=2, col=1)
            # Add upper/lower bounds
            fig.update_yaxes(range=[-10, 110], row=2, col=1)
            fig.add_hline(y=0, col=1, row=2, line_color="#666", line_width=2)
            fig.add_hline(y=100, col=1, row=2, line_color="#666", line_width=2)
            # Add overbought/oversold
            fig.add_hline(y=30, col=1, row=2, line_color='#336699',
                          line_width=2, line_dash='dash')
            fig.add_hline(y=70, col=1, row=2, line_color='#336699',
                          line_width=2, line_dash='dash')

            # MACD
            # Fast Signal (%k)
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['execute_buy'],
                    name='Buy Action',
                    # showlegend=False,
                    legendgroup='2',
                    mode="markers",
                    marker=dict(
                        color='green',
                        line=dict(color='green', width=2),
                        symbol='triangle-down',
                    ),
                ), row=1, col=1
            )
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['execute_sell'],
                    name='Sell Action',
                    # showlegend=False,
                    legendgroup='2',
                    mode="markers",
                    marker=dict(
                        color='red',
                        line=dict(color='red', width=2),
                        symbol='triangle-up',
                    ),
                ), row=1, col=1
            )
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['macd'],
                    line=dict(color='#ff9900', width=2),
                    name='macd',
                    # showlegend=False,
                    legendgroup='2',
                ), row=3, col=1
            )
            # Slow signal (%d)
            fig.append_trace(
                go.Scatter(
                    x=df.index,
                    y=df['macd_s'],
                    line=dict(color='#000000', width=2),
                    # showlegend=False,
                    legendgroup='2',
                    name='signal'
                ), row=3, col=1
            )
            # Colorize the histogram values
            colors = np.where(df['macd_h'] < 0, 'red', 'green')
            # Plot the histogram
            fig.append_trace(
                go.Bar(
                    x=df.index,
                    y=df['macd_h'],
                    name='histogram',
                    marker_color=colors,
                ), row=3, col=1
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
