import numpy as np
import pandas as pd


class Tester(object):

    def test(self, df, balance):

        # budget = 100_000
        def test_strategy(df, balance):
            print("balance before strategy: ", balance)
            is_long = False
            is_short = False
            size = 0
            last_value = None
            for index, row in df.iterrows():
                if row.predicted_signal == 1:
                    if is_long == True:
                        continue
                    if is_short == True:
                        # close the short position
                        balance += size * row.close
                        size = 0
                        is_short = False
                    # create long position
                    is_long = True

                    size = balance // row.close
                    balance -= size * row.close

                elif row.predicted_signal == -1:
                    if is_short == True:
                        continue
                    if is_long == True:
                        # close the long position
                        balance += size * row.close
                        size = 0
                        is_long = False
                    # create short position
                    is_short = True

                    size = -balance // row.close
                    balance -= size * row.close

                last_value = row.close

            balance += size * last_value
            print("balance after the strategy is: ", balance)
            return balance

        return test_strategy(df, balance)
