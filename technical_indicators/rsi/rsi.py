import pandas as pd
import numpy as np


class RSI:
    def calculate(self, df: pd.DataFrame):
        df.ta.rsi(close='close', length=14, append=True)
