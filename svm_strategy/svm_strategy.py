import pandas as pd
import numpy as np

from place_order.place_order import PlaceOrder

from technical_indicators.technical_indicators import TechnicalIndicators as TI


class SVMStrategy(object):
    def __init__(self, df, model, fileToSave, app, contract, budget):
        self.df = df
        self.model = model
        self.last_timestamp = None
        self.fileToSave = fileToSave
        self.app = app
        self.contract = contract
        self.budget = budget
        self.is_long = False
        self.is_short = False
        self.short_pos_qty = 0
        self.long_pos_qty = 0
        self.latest_data = []
        print("budget before strategy: ", self.budget)

    def executeTrade(self, reqId, bar):
        print(reqId, bar)

        if self.last_timestamp is None or self.last_timestamp == bar.date:
            self.last_timestamp = bar.date
            # Trigger new trading operation
            self.latest_data = [[int(bar.date), float(bar.open), float(bar.close), float(
                bar.high), float(bar.low), float(bar.volume)]]
        else:
            data = self.latest_data
            print("Time to run execution on:", data)
            temp_df = pd.DataFrame(data=np.array(data), columns=[
                "date", "open", "close", "high", "low", "volume"])
            df = pd.concat([self.df, temp_df], ignore_index=True)
            df = TI(candlestickData=None,
                    fileToSave=None).process_data_with_file(df)

            df['open-close'] = (df.open - df.close) / df.open
            df['open-close-1'] = df['open-close'].shift(1)
            df['open-close-2'] = df['open-close'].shift(2)
            df['open-close-3'] = df['open-close'].shift(3)
            df['high-low'] = (df.high - df.low) / df.low
            df['high-low-1'] = df['high-low'].shift(1)
            df['high-low-2'] = df['high-low'].shift(2)
            df['high-low-3'] = df['high-low'].shift(3)
            df['EMA_delta'] = df.close - df.EMA_10
            df['SMA_200_50'] = df.SMA_200 - df.SMA_50

            print("Last 5 rows of df during live testing: ", df.tail(5))

            X = df.tail(1)[['open-close', 'high-low', 'RSI_14', 'minus_di',
                            'plus_di', 'adx', 'EMA_delta', 'SMA_200_50', 'open-close-1', 'open-close-2', 'open-close-3', 'high-low-1', 'high-low-2', 'high-low-3']]
            print("Asking prediction for:", X)
            prediction = self.model.predict(X)

            print("prediction is: ", prediction[0])
            # budget = 100_000
            print("passing price: ", df.tail(1).open.values[0])
            self.order(prediction, df.tail(
                1).open.values[0], df.tail(1).date.values[0])

            self.last_timestamp = bar.date
            data = [[int(bar.date), float(bar.open), float(bar.close), float(
                bar.high), float(bar.low), float(bar.volume)]]
            self.df = df

    def order(self, prediction, price, date):
        if prediction == 1:
            if self.is_long == True:
                return
            if self.is_short == True:
                # close the short position
                self.budget += self.short_pos_qty * price
                print("closing short position at index:",
                      date, ", balance is now: ", self.budget)
                ########################### PLACE ORDER #################################
                place_order = PlaceOrder(self.app)
                place_order.execute_order(
                    self.contract,
                    place_order.get_order(action='BUY', qty=-self.short_pos_qty,
                                          order_type='MKT')
                )
                ########################### PLACE ORDER #################################
                self.short_pos_qty = 0
                self.is_short = False
            # create long position
            self.is_long = True
            self.long_pos_qty = self.budget // price
            self.budget -= self.long_pos_qty * price
            print("opening long position at index:",
                  date, ", balance is now: ", self.budget)
            ########################### PLACE ORDER #################################
            place_order = PlaceOrder(self.app)
            place_order.execute_order(
                self.contract,
                place_order.get_order(action='BUY', qty=self.long_pos_qty,
                                      order_type='MKT')
            )
            ########################### PLACE ORDER #################################
        elif prediction == -1:
            if self.is_short == True:
                return
            if self.is_long == True:
                # close the long position
                self.budget += self.long_pos_qty * price
                print("closing long position at index:",
                      date, ", balance is now: ", self.budget)
                ########################### PLACE ORDER #################################
                place_order = PlaceOrder(self.app)
                place_order.execute_order(
                    self.contract,
                    place_order.get_order(action='SELL', qty=self.long_pos_qty,
                                          order_type='MKT')
                )
                ########################### PLACE ORDER #################################
                self.long_pos_qty = 0
                self.is_long = False
            # create short position
            self.is_short = True
            self.short_pos_qty = -self.budget // price
            self.budget -= self.short_pos_qty * price
            ########################### PLACE ORDER #################################
            place_order = PlaceOrder(self.app)
            place_order.execute_order(
                self.contract,
                place_order.get_order(action='SELL', qty=-self.short_pos_qty,
                                      order_type='MKT')
            )
            ########################### PLACE ORDER #################################
            print("opening short position at index:",
                  date, ", balance is now: ", self.budget)
