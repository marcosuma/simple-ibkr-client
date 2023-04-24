from backtesting import Strategy


class BacktestingStrategy(Strategy):
    def init(self):
        super().init()

    def next(self):
        super().next()
        if self.data.rsi_execute_buy[-1] == 1:
            if self.position and self.position.is_long:
                return
            self.buy()
        elif self.data.rsi_execute_sell[-1] == 1:
            if self.position and self.position.is_short:
                return
            self.sell()
