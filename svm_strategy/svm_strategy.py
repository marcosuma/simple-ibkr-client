import pandas as pd
import numpy as np

from ibapi.contract import Contract

from trader.trader import Trader

from technical_indicators.technical_indicators import TechnicalIndicators as TI


class SVMStrategy(object):
    def __init__(self, df, model, fileToSave, app, contract: Contract, trader: Trader):
        self.df = df
        self.model = model
        self.last_timestamp = None
        self.fileToSave = fileToSave
        self.app = app
        self.contract = contract
        self.is_long = False
        self.is_short = False
        self.short_pos_qty = 0
        self.long_pos_qty = 0
        self.latest_data = []
        self.trader = trader

    def executeTrade(self, reqId, bar):
        print(reqId, bar)

        if self.last_timestamp is None or self.last_timestamp == bar.date:
            self.last_timestamp = bar.date
            # Trigger new trading operation
            self.latest_data = [
                [
                    int(bar.date),
                    float(bar.open),
                    float(bar.close),
                    float(bar.high),
                    float(bar.low),
                    float(bar.volume),
                ]
            ]
        else:
            data = self.latest_data
            print("Time to run execution on:", data)
            temp_df = pd.DataFrame(
                data=np.array(data),
                columns=["date", "open", "close", "high", "low", "volume"],
            )
            df = pd.concat([self.df, temp_df], ignore_index=True)
            df = TI(candlestickData=None, fileToSave=None).process_data_with_file(df)

            df["open-close"] = (df.open - df.close) / df.open
            df["open-close-1"] = df["open-close"].shift(1)
            df["open-close-2"] = df["open-close"].shift(2)
            df["open-close-3"] = df["open-close"].shift(3)
            df["high-low"] = (df.high - df.low) / df.low
            df["high-low-1"] = df["high-low"].shift(1)
            df["high-low-2"] = df["high-low"].shift(2)
            df["high-low-3"] = df["high-low"].shift(3)
            df["EMA_delta"] = df.close - df.EMA_10
            df["SMA_200_50"] = df.SMA_200 - df.SMA_50

            print("Last 5 rows of df during live testing: ", df.tail(5))

            X = df.tail(1)[
                [
                    "open-close",
                    "high-low",
                    "RSI_14",
                    "minus_di",
                    "plus_di",
                    "adx",
                    "EMA_delta",
                    "SMA_200_50",
                    "open-close-1",
                    "open-close-2",
                    "open-close-3",
                    "high-low-1",
                    "high-low-2",
                    "high-low-3",
                ]
            ]
            print("Asking prediction for:", X)
            prediction = self.model.predict(X)

            print("prediction is: ", prediction[0])
            print("passing price: ", bar.open)
            atr = df.tail(1)[["atr"][0]].values[0]
            self.order(prediction, bar.open, bar.date, atr)

            self.last_timestamp = bar.date
            data = [
                [
                    int(bar.date),
                    float(bar.open),
                    float(bar.close),
                    float(bar.high),
                    float(bar.low),
                    float(bar.volume),
                ]
            ]
            self.df = df

    def order(self, prediction, price, date, atr):
        if prediction == 1:
            # if self.trader.isLong(self.contract.symbol) == True:
            #     return
            print(
                "trying to open long position at index:", date, ", with price: ", price
            )
            self.trader.buy(
                self.contract,
                "LMT",
                quantity=None,
                close_existing_positions=True,
                limit_price=price,
                stop_loss=price - 2 * atr,
                target_profit=price + 7 * atr,
            )
        elif prediction == -1:
            # if self.trader.isShort(self.contract.symbol) == True:
            #     return
            print(
                "trying to open short position at index:", date, ", with price: ", price
            )
            self.trader.sell(
                self.contract,
                "LMT",
                quantity=None,
                close_existing_positions=True,
                limit_price=price,
                stop_loss=price + 2 * atr,
                target_profit=price - 7 * atr,
            )
