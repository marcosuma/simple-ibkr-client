import numpy as np
import pandas as pd


class Tester(object):

    # sl_range = 1 - np.arange(0.01, 0.1, 0.01)
    # tp_range = 1 + np.arange(0.01, 0.25, 0.01)
    def test_with_sl_and_pt(self, df):
        def test_strategy(df):
            in_position = False
            is_long = None

            buydates, selldates = [], []
            buyprices, sellprices = [], []
            long_short = []

            for index, row in df.iterrows():
                if not in_position and row.execute_buy != "NaN":
                    buyprice = row.shifted_open
                    buydates.append(index)
                    buyprices.append(buyprice)
                    in_position = True
                    is_long = True
                    long_short.append("Long")
                    sl = row.open - 2 * row.STDEV_30
                    tp = row.open + 10 * row.STDEV_30
                    # print('stop loss: ' + str(sl) +
                    #       ' target profit: ' + str(tp))
                    continue
                if not in_position and row.execute_sell != "NaN":
                    sellprice = row.shifted_open
                    selldates.append(index)
                    sellprices.append(sellprice)
                    in_position = True
                    is_long = False
                    long_short.append("Short")
                    tp = row.open - 10 * row.STDEV_30
                    sl = row.open + 2 * row.STDEV_30
                    # print('stop loss: ' + str(sl) +
                    #       ' target profit: ' + str(tp))
                    continue
                if in_position:
                    if is_long:
                        if row.low < buyprice * sl:
                            sellprice = row.low
                            sellprices.append(sellprice)
                            selldates.append(index)
                        elif row.high > buyprice * tp:
                            sellprice = row.high
                            sellprices.append(sellprice)
                            selldates.append(index)
                    else:
                        if row.low < sellprice * sl:
                            buyprice = row.low
                            buyprices.append(buyprice)
                            buydates.append(index)
                        elif row.high > sellprice * tp:
                            buyprice = row.high
                            buyprices.append(buyprice)
                            buydates.append(index)
                    is_long = None
                    in_position = False

            profits = pd.Series(
                # 0.0015 is a fictitious fee
                [
                    (sell - buy) / buy - 0.0015
                    for sell, buy in zip(sellprices, buyprices)
                ],
                dtype="float64",
            )
            print("profit is: ", (profits + 1).prod())
            return profits, buydates, selldates, buyprices, sellprices, long_short

        return test_strategy(df)
