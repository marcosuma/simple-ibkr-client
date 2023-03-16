from backtesting import Strategy


class SVMStrategy(Strategy):
    def init(self):
        super().init()

    def next(self):
        super().next()
        if self.data.predicted_signal == 1:
            # sl = self.data.close[-1] * (1 - 2 * self.data.open_std)
            # tp = self.data.close[-1] * (1 + 10 * self.data.open_std)
            # self.buy(sl=sl, tp=tp)
            if self.position and self.position.is_long:
                return
            # if self.position and self.position.is_short:
            #     self.position.close()
            order = self.buy()
            print("Go long. New order is: ", order)
            print(self.trades)
        elif self.data.predicted_signal == -1:
            # sl = self.data.close[-1] * (1 + 2 * self.data.open_std)
            # tp = self.data.close[-1] * (1 - 10 * self.data.open_std)
            # self.sell(sl=sl, tp=tp)
            if self.position and self.position.is_short:
                return
            # if self.position and self.position.is_long:
            #     self.position.close()
            order = self.sell()
            print("Go short. New order is: ", order)
            print(self.trades)
