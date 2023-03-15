import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Plot(object):

    def __init__(self, df, plotsQueue):
        self.df = df
        self.plotsQueue = plotsQueue

    def plot(self):
        df = self.df
        plotsQueue = self.plotsQueue
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
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['execute_buy'],
            #         name='Buy Action',
            #         # showlegend=False,
            #         legendgroup='2',
            #         mode="markers",
            #         marker=dict(
            #             color='green',
            #             line=dict(color='green', width=2),
            #             symbol='triangle-down',
            #         ),
            #     ), row=1, col=1
            # )
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['execute_sell'],
            #         name='Sell Action',
            #         # showlegend=False,
            #         legendgroup='2',
            #         mode="markers",
            #         marker=dict(
            #             color='red',
            #             line=dict(color='red', width=2),
            #             symbol='triangle-up',
            #         ),
            #     ), row=1, col=1
            # )
            # # EMA 10
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['EMA_10'],
            #         line=dict(color='black', width=2),
            #         name='EMA 10',
            #         # showlegend=False,
            #         legendgroup='2',
            #     ), row=1, col=1
            # )
            # # Bollinger up
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['bollinger_up'],
            #         line=dict(color='blue', width=2),
            #         name='BB_up',
            #         # showlegend=False,
            #         legendgroup='2',
            #     ), row=1, col=1
            # )
            # # Bollinger down
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['bollinger_down'],
            #         line=dict(color='blue', width=2),
            #         name='BB_down',
            #         # showlegend=False,
            #         legendgroup='2',
            #     ), row=1, col=1
            # )

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

            # # MACD
            # # Fast Signal (%k)
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['macd'],
            #         line=dict(color='#ff9900', width=2),
            #         name='macd',
            #         # showlegend=False,
            #         legendgroup='2',
            #     ), row=3, col=1
            # )
            # # Slow signal (%d)
            # fig.append_trace(
            #     go.Scatter(
            #         x=df.index,
            #         y=df['macd_s'],
            #         line=dict(color='#000000', width=2),
            #         # showlegend=False,
            #         legendgroup='2',
            #         name='signal'
            #     ), row=3, col=1
            # )
            # # Colorize the histogram values
            # colors = np.where(df['macd_h'] < 0, 'red', 'green')
            # # Plot the histogram
            # fig.append_trace(
            #     go.Bar(
            #         x=df.index,
            #         y=df['macd_h'],
            #         name='histogram',
            #         marker_color=colors,
            #     ), row=3, col=1
            # )

            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['adx'],
                line=dict(color='blue', width=2),
                showlegend=False), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['plus_di'],
                line=dict(color='green', width=2),
                showlegend=False), row=3, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['minus_di'],
                line=dict(color='red', width=2),
                showlegend=False), row=3, col=1)


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

        plotsQueue.append(plotFn)

    