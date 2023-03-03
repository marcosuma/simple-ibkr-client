import pandas as pd
import pandas_ta


class EMA:
    def calculate(self, df: pd.DataFrame):
        df.ta.ema(close='close', length=10, append=True)
        # df.ta.ema(close='close', length=60, append=True)
