from ibapi.ticktype import TickTypeEnum


class Callback():
    def __init__(self, priceByTime):
        self.priceByTime = priceByTime

    def handleAlibaba(self, reqId, bar):
        print("Alibaba data")
        self._handleBase(reqId, bar)

    def handleEnel(self, reqId, bar):
        print("Enel data")
        self._handleBase(reqId, bar)

    def handleGld(self, reqId, bar):
        print("Gld data")
        self._handleBase(reqId, bar)

    def handleEurUsd(self, reqId, bar):
        print("EUR/USD data")
        self._handleBase(reqId, bar)

    def handleBitcoinFutures(self, reqId, bar):
        print("Bitcoin Futures data")
        self._handleBase(reqId, bar)

    def _handleBase(self, reqId, bar):
        print(reqId, bar)
        self.priceByTime[bar.date] = [bar.date, bar.close]
