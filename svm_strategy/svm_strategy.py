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
        self.is_long = None
        self.short_pos_qty = 0
        self.long_pos_qty = 0
        print("budget before strategy: ", self.budget)

    def executeTrade(self, reqId, bar):
        print(reqId, bar)

        if self.last_timestamp != bar.date:
            self.last_timestamp = bar.date
            # Trigger new trading operation
            data = [[int(bar.date), float(bar.open), float(bar.close), float(
                bar.high), float(bar.low), float(bar.volume)]]
            temp_df = pd.DataFrame(data=np.array(data), columns=[
                "date", "open", "close", "high", "low", "volume"])
            df = pd.concat([self.df, temp_df], ignore_index=True)
            df = TI(None, self.fileToSave).process_data_with_file(df)
            df['open-close'] = df.open - df.close
            df['high-low'] = df.high - df.low

            X = df.tail(1)[['open-close', 'high-low', 'RSI_14',
                            'minus_di', 'plus_di', 'adx']]
            prediction = self.model.predict(X)

            print("prediction is: ", prediction[0])

            ########################### PLACE ORDER #################################
            # place_order = PlaceOrder(self.app)
            # place_order.execute_order(
            #     self.contract,
            #     place_order.get_order(action='SELL', qty=10000,
            #                           order_type='MKT')
            # )
            ########################### PLACE ORDER #################################
            # budget = 100_000
            print("passing price: ", df.tail(1).open.values[0])
            self.order(prediction, df.tail(
                1).open.values[0], df.tail(1).date.values[0])

    def order(self, prediction, price, date):
        if prediction == 1:
            if self.is_long == True:
                return
            if self.is_long == False:
                # close the short position
                self.budget -= self.short_pos_qty * price
                print("closing short position at index:",
                      date, ", balance is now: ", self.budget)
                self.short_pos_qty = 0
            # create long position
            self.is_long = True
            self.long_pos_qty = self.budget // price
            self.budget -= self.long_pos_qty * price
            print("opening long position at index:",
                  date, ", balance is now: ", self.budget)
        elif prediction == -1:
            if self.is_long == False:
                return
            if self.is_long == True:
                # close the long position
                self.budget += self.long_pos_qty * price
                print("closing long position at index:",
                      date, ", balance is now: ", self.budget)
                self.long_pos_qty = 0
            # create short position
            self.is_long = False
            self.short_pos_qty = self.budget // price
            self.budget += self.short_pos_qty * price
            print("opening short position at index:",
                  date, ", balance is now: ", self.budget)
