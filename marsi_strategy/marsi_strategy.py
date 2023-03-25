import numpy as np
from marsi_strategy.tester import Tester


class MARSIStrategy(object):

    def execute(self, df):
        rsi_above_70 = np.where(df['RSI_14'] >= 70, True, False)
        rsi_below_30 = np.where(df['RSI_14'] <= 30, True, False)
        hist = 7
        for i in range(hist, len(df.index)-hist):
            df.loc[i, 'RSI_30_ok'] = True \
                if rsi_below_30[i - hist:i].sum() > 0 \
                else False
            df.loc[i, 'RSI_70_ok'] = True \
                if rsi_above_70[i - hist:i].sum() > 0 \
                else False
            
        df['macd_trend'] = np.where(df['macd'] < df['macd_s'], -1, 1)
        df['macd_buy_signal'] = np.sign(df['macd_trend']).diff().gt(0)
        df['macd_sell_signal'] = np.sign(df['macd_trend']).diff().lt(0)

        df['execute_buy'] = np.where(
            df['macd_buy_signal'] & df['RSI_30_ok'], df['close'] + df['close_std'], "NaN")
        df['execute_sell'] = np.where(
            df['macd_sell_signal'] & df['RSI_70_ok'], df['close'] - df['close_std'], "NaN")

        profits, buydates, selldates, buyprices, sellprices, long_short = Tester(
        ).test_with_sl_and_pt(df)

        # for x in zip(profits, buydates, selldates, buyprices, sellprices, long_short):
        #     print(x)
