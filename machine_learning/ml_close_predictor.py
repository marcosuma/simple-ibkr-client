import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt


class MachineLearning:
    def __init__(self, candlestickData, plotsQueue):
        self.candlestickData = candlestickData
        self.plotsQueue = plotsQueue
        pass

    # Uses LSTM (Long Short Term Memory) to predict the closing price of an asset
    # Uses past 60 days
    def process_data(self, reqId: int, start: str, end: str):
        df = pd.DataFrame(
            data=np.array(self.candlestickData),
            columns=["date", "open", "close", "high", "low", "volume"],
        )

        print(df)

        data = df.filter(["close"])
        dataset = data.to_numpy(dtype="float64")
        training_data_len = math.ceil(len(dataset) * 0.8)

        # Scale the data
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        train_data = scaled_data[0 : training_data_len - 8, :]
        x_train = []
        y_train = []

        for i in range(60, len(train_data) - 8):
            x_train.append(train_data[i - 60 : i, 0])
            y_train.append(train_data[i + 8, 0])
            # if i <= 60:
            #     print(x_train)
            #     print(y_train)
            #     print()

        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

        try:
            import os

            model = load_model(
                os.path.dirname(os.path.abspath(__file__)) + "/models/model_1"
            )
            print("Model correctly loaded")
        except OSError:
            # if model is None:
            model = Sequential()
            model.add(
                LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1))
            )
            model.add(LSTM(50, return_sequences=False))
            model.add(Dense(25))
            model.add(Dense(1))

            model.compile(optimizer="adam", loss="mean_squared_error")

            model.fit(x_train, y_train, batch_size=32, epochs=2)

            model.save(os.path.dirname(os.path.abspath(__file__)) + "/models/model_1")

        # Create test dataset
        test_data = scaled_data[training_data_len - 60 : -8, :]
        x_test = []
        y_test = dataset[training_data_len + 8 :, :]

        for i in range(60, len(test_data)):
            x_test.append(test_data[i - 60 : i, 0])

        x_test = np.array(x_test)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        predictions = model.predict(x_test)
        predictions = scaler.inverse_transform(predictions)

        rmse = np.sqrt(np.mean(predictions - y_test) ** 2)
        # Print RMSE results
        print(rmse)

        train = data[:training_data_len]
        valid = data[training_data_len:-8]
        valid["predictions"] = predictions

        print(valid)

        def plotFn():
            # visualize the model
            plt.figure(figsize=(16, 8))
            plt.title("Model")
            plt.xlabel("Date", fontsize=18)
            plt.ylabel("Close price", fontsize=18)

            plt.plot(pd.to_numeric(train["close"]))
            plt.plot(pd.to_numeric(valid["close"]))
            plt.plot(valid["predictions"])

            plt.legend(["Train", "Val", "Predictions"], loc="lower right")

            plt.show()

        self.plotsQueue.append(plotFn)
