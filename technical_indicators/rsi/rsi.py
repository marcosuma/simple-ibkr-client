import pandas as pd
import numpy as np


class RSI:
    def calculate(self, df: pd.DataFrame):
        df.ta.rsi(close='close', length=14, append=True)

        rsi_above_70 = np.where(df['RSI_14'] >= 70, True, False)
        rsi_below_30 = np.where(df['RSI_14'] <= 30, True, False)
        df['RSI_30_ok'] = rsi_below_30
        df['RSI_70_ok'] = rsi_above_70

        hist = 5
        for i in range(hist, len(df.index)-hist):
            df['RSI_30_ok'][i] = True \
                if rsi_below_30[i - hist:i].sum() > 0 \
                else False
            df['RSI_70_ok'][i] = True \
                if rsi_above_70[i - hist:i].sum() > 0 \
                else False
