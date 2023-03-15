import numpy as np
import pandas as pd


class Tester(object):

    def test(self, df, balance):

        # budget = 100_000
        def test_strategy(df, balance):
            print("balance before strategy: ", balance)
            is_long = None
            short_pos_qty, long_pos_qty = 0, 0
            last_value = None

            for index, row in df.iterrows():
                if row.predicted_signal == 1:
                    if is_long == True:
                        continue
                    if is_long == False:
                        # close the short position
                        balance -= short_pos_qty * row.open
                        print("closing short position at index:",
                              index, ", balance is now: ", balance)
                        short_pos_qty = 0
                    # create long position
                    is_long = True

                    long_pos_qty = balance // row.open
                    balance -= long_pos_qty * row.open
                    print("opening long position at index:",
                          index, ", balance is now: ", balance)

                elif row.predicted_signal == -1:
                    if is_long == False:
                        continue
                    if is_long == True:
                        # close the long position
                        balance += long_pos_qty * row.open
                        print("closing long position at index:",
                              index, ", balance is now: ", balance)
                        long_pos_qty = 0
                    # create short position
                    is_long = False

                    short_pos_qty = balance // row.open
                    balance += short_pos_qty * row.open
                    print("opening short position at index:",
                          index, ", balance is now: ", balance)

                last_value = row.close

            balance += short_pos_qty * last_value
            balance += long_pos_qty * last_value
            print("balance after the strategy is: ", balance)
            return balance

        return test_strategy(df, balance)
