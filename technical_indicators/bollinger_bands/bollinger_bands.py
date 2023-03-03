import pandas as pd
import pandas_ta


class BollingerBands:
    def calculate(self, df: pd.DataFrame):
        rate = 20
        sma = self._get_sma(df['close'], rate)  # <-- Get SMA for 20 days
        # <-- Get rolling standard deviation for 20 days
        std = df['close'].rolling(rate).std()
        bollinger_up = sma + std * 2  # Calculate top band
        bollinger_down = sma - std * 2  # Calculate bottom band
        df['bollinger_up'] = bollinger_up
        df['bollinger_down'] = bollinger_down

    def _get_sma(self, prices, rate):
        return prices.rolling(rate).mean()
