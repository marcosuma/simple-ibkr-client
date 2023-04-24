import numpy as np
import pandas as pd

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from tester.tester import Tester as MyBacktest

import os
import pickle

from backtesting import Backtest
from machine_learning.svm_backtesting.svm_strategy import SVMStrategy


class SVMModelTrainer(object):

    def __init__(self, plotsQueue, fileToSave):
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def process_data_with_file(self, df):
        df, predictions = self.__fn_impl(df)
        # df.to_csv(self.fileToSave)
        return df, predictions

    def __fn_impl(self, _df: pd.DataFrame):
        df = _df.copy()
        # Changes The Date column as index columns
        from datetime import datetime
        df['date'] = df.apply(lambda row: datetime.utcfromtimestamp(
            row.date).strftime('%Y-%m-%d %H:%M:%S'), axis=1)
        df.index = pd.to_datetime(df['date'])

        # drop The original date column
        df = df.drop(['date'], axis='columns')

        # Create predictor variables
        df['open-close'] = (df.open - df.close) / df.open
        df['high-low'] = (df.high - df.low) / df.low
        df['open-close-1'] = df['open-close'].shift(1)
        df['open-close-2'] = df['open-close'].shift(2)
        df['open-close-3'] = df['open-close'].shift(3)
        df['high-low-1'] = df['high-low'].shift(1)
        df['high-low-2'] = df['high-low'].shift(2)
        df['high-low-3'] = df['high-low'].shift(3)
        df['EMA_delta'] = df.close - df.EMA_10
        df['SMA_200_50'] = df.SMA_200 - df.SMA_50
        df.dropna(inplace=True)

        # Target variables
        y = np.where(df['close'] < df['close'].shift(-1), 1, -1)

        # Store all predictor variables in a variable X
        X = df[['open-close', 'high-low', 'RSI_14', 'minus_di',
                'plus_di', 'adx', 'EMA_delta', 'SMA_200_50', 'open-close-1', 'open-close-2', 'open-close-3', 'high-low-1', 'high-low-2', 'high-low-3']]

        split = int(0.6*len(df))
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
            model = SVC(gamma='auto')
            model = model.fit(X_train, y_train)
            pickle.dump(model, open(model_filename_path, 'wb'))

        df['predicted_signal'] = model.predict(X)
        print("predicted_signal: ", df['predicted_signal'].value_counts())

        y_pred = model.predict(X_test)
        print("Test accuracy: ", accuracy_score(y_test, y_pred))

        cash = 100_000

        df['Open'] = df.open
        df['Close'] = df.close
        df['High'] = df.high
        df['Low'] = df.low

        bt_df = df.iloc[split:].copy()
        buy_pred_fn = lambda row: row.predicted_signal == 1
        sell_pred_fn = lambda row: row.predicted_signal == -1
        MyBacktest().test(bt_df, cash, buy_pred_fn, sell_pred_fn)
        bt = Backtest(bt_df, SVMStrategy, cash=cash, commission=0.0002,
                      exclusive_orders=True)
        stat = bt.run()
        print(stat)

        # Calculate daily returns
        bt_df['return'] = np.log(bt_df.close.div(bt_df.close.shift(1)))

        # Calculate strategy returns
        bt_df['strategy_return'] = bt_df['return'] * bt_df.predicted_signal.shift(1)

        bt_df["cum_ret"] = bt_df["return"].cumsum().apply(np.exp)
        bt_df["cum_strategy"] = bt_df["strategy_return"].cumsum().apply(np.exp)        

        def plotFn():
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True)
            fig.add_trace(go.Scatter(
                x=bt_df.index,
                y=bt_df['cum_ret'],
                line=dict(color='red', width=2),
                showlegend=False), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=bt_df.index,
                y=bt_df['cum_strategy'],
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
