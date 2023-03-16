import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import os


class MLAveragePredictor:

    def __init__(self, plotsQueue, fileToSave):
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    def process_data_with_file(self, df):
        df, predictions = self.__fn_impl(df)
        df.to_csv(self.fileToSave)
        return df, predictions

    def __fn_impl(self, df: pd.DataFrame):
        hist_len = 10  # ticks
        future_len = 5  # ticks
        df.dropna(inplace=True)
        data = df.filter(['close', 'open', 'high', 'low', 'SMA_50', 'SMA_100', 'SMA_200',
                         'EMA_10', 'RSI_14', 'Macd', 'Macd_h', 'Macd_s', 'Bollinger_up', 'Bollinger_down'])
        dataset = data.to_numpy(dtype='float64')
        training_data_len = math.ceil(len(dataset) * .8)

        # Scale the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)
        target_scaler = MinMaxScaler(feature_range=(0, 1))
        target_scaled_data = target_scaler.fit_transform(
            np.reshape(dataset[:, 4], (-1, 1)))

        train_data = scaled_data[0:training_data_len, :]
        test_data = scaled_data[training_data_len-hist_len:, :]
        x_train = []
        y_train = []
        # Create test dataset
        x_test = []
        y_test = []

        for i in range(hist_len, len(train_data) - future_len):
            x_train.append(train_data[i-hist_len:i, :])
            y_train.append(train_data[i+future_len, 4])  # 4 = SMA_50

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(
            x_train, (x_train.shape[0], x_train.shape[1], x_train.shape[2]))
        y_train = np.reshape(y_train, (y_train.shape[0], 1))

        for i in range(hist_len, len(test_data) - future_len):
            x_test.append(test_data[i-hist_len:i, :])
            y_test.append(test_data[i+future_len, 4])  # 4 = SMA_50

        x_test, y_test = np.array(x_test), np.array(y_test)
        x_test = np.reshape(
            x_test, (x_test.shape[0], x_test.shape[1], x_test.shape[2]))
        y_test = np.reshape(y_test, (y_test.shape[0], 1))

        model_filename_path = "/models/{}-{}".format(
            self.fileToSave.split(".")[0], os.path.basename(__file__).split(".")[0])
        try:
            model = load_model(os.path.dirname(
                os.path.abspath(__file__)) + model_filename_path)
            print("Model correctly loaded")
        except OSError:
            model = Sequential()
            model.add(LSTM(50, return_sequences=True,
                           input_shape=(x_train.shape[1], x_train.shape[2])))
            model.add(LSTM(50, return_sequences=False))
            model.add(Dense(25))
            model.add(Dense(25))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mean_squared_error')
            model.fit(x_train, y_train, batch_size=32, epochs=50)

            model.save(os.path.dirname(
                os.path.abspath(__file__)) + model_filename_path)

        predictions = model.predict(x_test)
        predictions = target_scaler.inverse_transform(predictions)

        rmse = np.sqrt(np.mean(predictions - y_test)**2)
        # Print RMSE results
        print(rmse)

        train = data[:training_data_len]
        valid = data[training_data_len:-future_len]
        print("---------------------PREDICTIONS--------------------------------")
        print(predictions)
        valid['predictions_SMA_50'] = predictions[:, 0]
        valid['predictions_SMA_50'] = valid.predictions_SMA_50.shift(
            future_len)

        def plotFn():
            # visualize the model
            plt.figure(figsize=(16, 8))
            plt.title('Model')
            plt.xlabel('Date', fontsize=18)
            plt.ylabel('Close price', fontsize=18)

            plt.plot(pd.to_numeric(train['close']))
            plt.plot(pd.to_numeric(train['SMA_50']))
            plt.plot(pd.to_numeric(valid['close']))
            plt.plot(pd.to_numeric(valid['SMA_50']))
            plt.plot(valid['predictions_SMA_50'])

            plt.legend(['Train close', 'Train SMA', 'Valid close',
                       'Valid SMA', 'Predictions'], loc='lower right')

            plt.show()

        self.plotsQueue.append(plotFn)

        return df, predictions
