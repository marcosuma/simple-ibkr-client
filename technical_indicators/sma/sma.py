import pandas as pd
import pandas_ta


class SMA:
    def calculate(self, df: pd.DataFrame):
        df['SMA_50'] = df.close.rolling(50).mean()
        df['SMA_100'] = df.close.rolling(100).mean()
        df['SMA_200'] = df.close.rolling(200).mean()

        # df['open_std'] = df.open.std()
        # df['close_std'] = df.close.std()
        df.ta.stdev(append=True)
