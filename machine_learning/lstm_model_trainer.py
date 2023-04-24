import numpy as np
import pandas as pd
import math
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Dropout

import plotly.graph_objects as go
from plotly.subplots import make_subplots


class LSTMModelTrainer:

    def __init__(self, plotsQueue, fileToSave):
        self.plotsQueue = plotsQueue
        self.fileToSave = fileToSave
        pass

    # Uses LSTM (Long Short Term Memory) to predict the closing price of an asset
    # Uses past 60 days
    def process_data(self, orig_df):        
        df = orig_df.dropna().copy()
        df['open_close'] = df['close'] - df['open']
        df['high_low'] = df['high'] - df['low']
        df['sma_diff'] = df['SMA_200'] - df['SMA_50']
        df['ema_delta'] = df.close - df.EMA_10
        data = df.filter(['close', 'open_close', 'high_low', 'SMA_50', 'SMA_200', 'EMA_10']).copy()
        dataset = data.to_numpy(dtype='float64')
        training_data_len = math.ceil(len(dataset) * .7)

        train_data = dataset[0:training_data_len, :]
        x_train = []
        y_train = []

        hist_len = 10

        for i in range(hist_len, len(train_data)-1):
            x_train.append(train_data[i-hist_len:i, 1:])
            y_train.append(0 if train_data[i, 0] > train_data[i+1, 0] else 1)

        scaler = MinMaxScaler(feature_range=(-1, 1))
        x_train, y_train = np.array(x_train), np.array(y_train)
        x_train = scaler.fit_transform(x_train.reshape(-1, x_train.shape[-1])).reshape(x_train.shape)
        x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], x_train.shape[2]))

        try :
            import os
            model = load_model(os.path.dirname(os.path.abspath(__file__)) + "/models/model_1")
            print("Model correctly loaded")
        except OSError:
            model = Sequential()
            model.add(LSTM(250, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
            model.add(LSTM(100, return_sequences=False))
            model.add(Dropout(0.2))
            model.add(Dense(1))

            model.compile(loss='mae', optimizer='adam')

            model.fit(x_train, y_train, batch_size=32, epochs=1, shuffle=False) 

            # model.save(os.path.dirname(os.path.abspath(__file__)) + "/models/model_1")

        test_data = dataset[training_data_len-hist_len:, :]
        x_test = []
        y_test = []

        for i in range(hist_len, len(test_data)-1):
            x_test.append(test_data[i-hist_len:i, 1:])
            y_test.append(0 if test_data[i, 0] > test_data[i+1, 0] else 1)
        
        x_test = np.array(x_test)
        # x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], x_train.shape[2]))
        x_test = scaler.fit_transform(x_test.reshape(-1, x_test.shape[-1])).reshape(x_test.shape)
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], x_test.shape[2]))

        predictions = model.predict(x_test)

        rmse = np.sqrt(np.mean(predictions - y_test)**2)
        # Print RMSE results
        print(rmse)


        train = data.iloc[:training_data_len].copy()
        valid = data.iloc[training_data_len:-1].copy()
        valid['predictions'] = predictions
        valid['y_test'] = y_test

        print(valid)
        valid.to_csv(os.path.dirname(os.path.abspath(__file__)) + "/models/results.csv")

        def plotFn():
            # visualize the model
            fig = make_subplots(rows=1, cols=1, shared_xaxes=True)

            fig.append_trace(
                go.Scatter(
                    x=valid.index,
                    y=valid.predictions,
                    line=dict(color='green', width=2),
                    name='Predictions',
                    mode="markers",
                    # showlegend=False
                ), row=1, col=1
            )
            fig.append_trace(
                go.Scatter(
                    x=valid.index,
                    y=valid.y_test,
                    line=dict(color='black', width=2),
                    name='Y Test',
                    mode="markers",
                    # showlegend=False
                ), row=1, col=1
            )

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








