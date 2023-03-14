import pandas as pd
import numpy as np


class RSI:
    def calculate(self, df: pd.DataFrame):
        df.ta.rsi(close='close', length=14, append=True)

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
