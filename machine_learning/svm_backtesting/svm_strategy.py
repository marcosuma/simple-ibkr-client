from backtesting import Strategy


class SVMStrategy(Strategy):
    def init(self):
        super().init()

    def next(self):
        super().next()
        if self.data.predicted_signal == 1:
            if self.position and self.position.is_long:
                return
            sl = self.data.open - 2 * self.data.open_std
            tp = self.data.open + 5 * self.data.open_std
            order = self.buy(sl=sl, tp=tp)
            # order = self.buy()
        elif self.data.predicted_signal == -1:
            if self.position and self.position.is_short:
                return
            sl = self.data.open + 2 * self.data.open_std
            tp = self.data.open - 5 * self.data.open_std
            # order = self.sell()
            order = self.sell(sl=sl, tp=tp)
