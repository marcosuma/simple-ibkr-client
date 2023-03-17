from backtesting import Strategy


class SVMStrategy(Strategy):
    def init(self):
        super().init()

    def next(self):
        super().next()
        if self.data.predicted_signal == 1:
            if self.position and self.position.is_long:
                return
            order = self.buy()
        elif self.data.predicted_signal == -1:
            if self.position and self.position.is_short:
                return
            order = self.sell()
