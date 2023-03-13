import numpy as np
from strategy.tester import Tester


class MARSIStrategy(object):

    def execute(self, df):
        df['execute_buy'] = np.where(
            df['macd_buy_signal'] & df['RSI_30_ok'], df['close'] + df['close_std'], "NaN")
        df['execute_sell'] = np.where(
            df['macd_sell_signal'] & df['RSI_70_ok'], df['close'] - df['close_std'], "NaN")

        profits, buydates, selldates, buyprices, sellprices, long_short = Tester(
        ).test_with_sl_and_pt(df)

        for x in zip(profits, buydates, selldates, buyprices, sellprices, long_short):
            print(x)
