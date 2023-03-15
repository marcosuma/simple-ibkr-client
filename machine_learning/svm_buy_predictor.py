import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score


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
            row.date).strftime('%Y-%m-%d'), axis=1)
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
        X = df[['open-close', 'high-low', 'RSI_14',
                'EMA_10', 'SMA_50', 'SMA_200', 'macd', 'macd_h', 'macd_s', 'bollinger_up', 'bollinger_down', 'minus_di', 'plus_di', 'adx']]
        X.head()

        # Target variables
        y = np.where(df['close'] > df['close'].shift(1), 1, -1)

        split = int(0.7*len(df))
        # Train data set
        X_train = X[:split]
        y_train = y[:split]

        # Test data set
        X_test = X[split:]
        y_test = y[split:]

        # Support vector classifier
        cls = SVC().fit(X_train, y_train)

        df['predicted_signal'] = cls.predict(X)

        y_pred = cls.predict(X_test)
        print("Test accuracy: ", accuracy_score(y_test, y_pred))

        # Calculate daily returns
        df['return'] = np.log(df.close.div(df.close.shift(1)))

        # Calculate strategy returns
        df['strategy_return'] = df['return'] * df.predicted_signal.shift(1)

        df["cum_ret"] = df["return"].cumsum().apply(np.exp)
        df["cum_strategy"] = df["strategy_return"].cumsum().apply(np.exp)

        # # Calculate Cumulutive returns
        # df['cum_ret'] = df['return'].cumsum()
        # # Plot Strategy Cumulative returns
        # df['cum_strategy'] = df['strategy_return'].cumsum()

        def plotFn():
            plt.figure(figsize=(16, 8))
            plt.title('Model')
            plt.xlabel('Date', fontsize=18)
            plt.ylabel('Close price', fontsize=18)

            plt.plot(df['cum_ret'], color='red')
            plt.plot(df['cum_strategy'], color='blue')

            plt.show()

        self.plotsQueue.append(plotFn)

        return _df, None
