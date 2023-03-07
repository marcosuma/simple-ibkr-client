import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import os


class MLCandlestickPredictor:

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
        print(df)

        self.__fn_impl(df)
        df.to_csv(self.fileToSave)

    def __fn_impl(self, df: pd.DataFrame):
        hist_len = 60  # days
        data = df.filter(['close', 'open', 'high', 'low'])
        dataset = data.to_numpy(dtype='float64')
        training_data_len = math.ceil(len(dataset) * .8)

        # Scale the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        train_data = scaled_data[0:training_data_len, :]
        x_train = []
        y_train = []

        # print(train_data[10-hist_len:10, :])

        for i in range(hist_len, len(train_data)):
            x_train.append(train_data[i-hist_len:i, :])
            y_train.append(train_data[i, :])

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(
            x_train, (x_train.shape[0], x_train.shape[1], 4))
        y_train = np.reshape(y_train, (y_train.shape[0], 4))
        model_filename_path = "/models/{}-{}".format(
            self.fileToSave, os.path.basename(__file__))
        try:
            model = load_model(os.path.dirname(
                os.path.abspath(__file__)) + model_filename_path)
            print("Model correctly loaded")
        except OSError:
            model = Sequential()
            model.add(LSTM(50, return_sequences=True,
                           input_shape=(x_train.shape[1], 4)))
            model.add(LSTM(50, return_sequences=False))
            model.add(Dense(25))
            model.add(Dense(4))
            model.compile(optimizer='adam', loss='mean_squared_error')
            model.fit(x_train, y_train, batch_size=32, epochs=2)

            model.save(os.path.dirname(
                os.path.abspath(__file__)) + model_filename_path)

        # Create test dataset
        test_data = scaled_data[training_data_len-hist_len:, :]
        x_test = []
        y_test = dataset[training_data_len:, :]

        for i in range(hist_len, len(test_data)):
            x_test.append(test_data[i-hist_len:i, :])

        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 4))
        y_test = np.reshape(y_test, (y_test.shape[0], 4))

        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)

        rmse = np.sqrt(np.mean(predictions - y_test)**2)
        # Print RMSE results
        print(rmse)

        train = data[:training_data_len]
        valid = data[training_data_len:]
        print("---------------------PREDICTIONS--------------------------------")
        print(predictions)
        valid['predictions_close'] = predictions[:, 0]
        valid['predictions_open'] = predictions[:, 1]
        valid['predictions_high'] = predictions[:, 2]
        valid['predictions_low'] = predictions[:, 3]

        print(valid)

        def plotFn():
            # visualize the model
            plt.figure(figsize=(16, 8))
            plt.title('Model')
            plt.xlabel('Date', fontsize=18)
            plt.ylabel('Close price', fontsize=18)

            plt.plot(pd.to_numeric(train['close']))
            plt.plot(pd.to_numeric(valid['close']))
            plt.plot(valid['predictions_close'])
            plt.plot(valid['predictions_open'])
            plt.plot(valid['predictions_high'])
            plt.plot(valid['predictions_low'])

            plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')

            plt.show()

        self.plotsQueue.append(plotFn)
