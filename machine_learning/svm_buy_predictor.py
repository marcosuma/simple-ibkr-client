import numpy as np
import pandas as pd

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import os
import pickle

from backtesting import Backtest
from machine_learning.svm_backtesting.svm_strategy import SVMStrategy


class SVMBuyPredictor:

    def __init__(self, plotsQueue, fileToSave):
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def process_data_with_file(self, df):
        df, predictions = self.__fn_impl(df)
        df.to_csv(self.fileToSave)
        return df, predictions

    def __fn_impl(self, _df: pd.DataFrame):
        df = _df.copy()
        # Changes The Date column as index columns
        from datetime import datetime
        df['date'] = df.apply(lambda row: datetime.utcfromtimestamp(
            row.date).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
        # df["date"] = df["date"].astype('datetime64[ns]')
        df.index = pd.to_datetime(df['date'])

        # drop The original date column
        df = df.drop(['date'], axis='columns')

        # Create predictor variables
        df['open-close'] = df.open.shift(1) - df.close.shift(1)
        df['high-low'] = df.high.shift(1) - df.low.shift(1)
        df['EMA_10'] = df['EMA_10'].shift(periods=1)
        df['SMA_50'] = df['SMA_50'].shift(periods=1)
        df['SMA_100'] = df['SMA_100'].shift(periods=1)
        df['SMA_200'] = df['SMA_200'].shift(periods=1)
        df['RSI_14'] = df['RSI_14'].shift(periods=1)
        df['macd'] = df['macd'].shift(periods=1)
        df['macd_h'] = df['macd_h'].shift(periods=1)
        df['macd_s'] = df['macd_s'].shift(periods=1)
        df['bollinger_up'] = df['bollinger_up'].shift(periods=1)
        df['bollinger_down'] = df['bollinger_down'].shift(periods=1)
        df['adx'] = df['adx'].shift(periods=1)
        df['plus_di'] = df['plus_di'].shift(periods=1)
        df['minus_di'] = df['minus_di'].shift(periods=1)

        df.dropna(inplace=True)

        # Store all predictor variables in a variable X
        X = df[['open-close', 'high-low', 'RSI_14', 'minus_di', 'plus_di', 'adx']]

        # Target variables
        y = np.where(df['close'] > df['close'].shift(1), 1, -1)

        split = int(0.9*len(df))
        # Train data set
        X_train = X[:split]
        y_train = y[:split]

        # Test data set
        X_test = X[split:]
        y_test = y[split:]

        model_filename_path = os.path.dirname(
            os.path.abspath(__file__)) + "/models/{}-{}.sav".format(
            self.fileToSave.split("/")[1].split(".")[0].strip(), os.path.basename(__file__).split(".")[0])
        try:
            model = pickle.load(open(model_filename_path, 'rb'))
            print("Model correctly loaded")
        except OSError:
            # Support vector classifier
            model = SVC()
            model = model.fit(X_train, y_train)
            pickle.dump(model, open(model_filename_path, 'wb'))

        df['predicted_signal'] = model.predict(X)

        y_pred = model.predict(X_test)
        print("Test accuracy: ", accuracy_score(y_test, y_pred))

        # Calculate daily returns
        df['return'] = np.log(df.close.div(df.close.shift(1)))

        # Calculate strategy returns
        df['strategy_return'] = df['return'] * df.predicted_signal.shift(1)

        df["cum_ret"] = df["return"].cumsum().apply(np.exp)
        df["cum_strategy"] = df["strategy_return"].cumsum().apply(np.exp)

        from machine_learning.tester import Tester
        Tester().test(df, 10_000)

        df['Open'] = df.open
        df['Close'] = df.close
        df['High'] = df.high
        df['Low'] = df.low
        bt = Backtest(df, SVMStrategy, cash=10_000,
                      commission=0.0002, exclusive_orders=True)
        stat = bt.run()
        print(stat)

        def plotFn():
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['cum_ret'],
                line=dict(color='red', width=2),
                showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['cum_strategy'],
                line=dict(color='blue', width=2),
                showlegend=False), row=1, col=1)

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

        return _df, model
