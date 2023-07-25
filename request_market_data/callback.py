from ibapi.ticktype import TickTypeEnum


class Callback:
    def __init__(self, askPriceMap, bidPriceMap):
        self.bidPriceMap = bidPriceMap
        self.askPriceMap = askPriceMap

    def handleMktDataAlibaba(self, reqId, tickType, price, attrib):
        print("Alibaba data")
        self._handleMktDataBase(reqId, tickType, price, attrib)

    def handleMktDataEnel(self, reqId, tickType, price, attrib):
        print("Enel data")
        self._handleMktDataBase(reqId, tickType, price, attrib)

    def handleDataEurUsd(self, reqId, tickType, price, attrib):
        print("EUR/USD data")
        self._handleMktDataBase(reqId, tickType, price, attrib)

    def handleDataBitcoinFutures(self, reqId, tickType, price, attrib):
        print("Bitcoin Futures data")
        self._handleMktDataBase(reqId, tickType, price, attrib)

    def _handleMktDataBase(self, reqId, tickType, price, attrib):
        if tickType == TickTypeEnum.ASK or tickType == TickTypeEnum.DELAYED_ASK:
            self.askPriceMap[reqId].append(price)
            print("ASK:", price)
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.DELAYED_BID:
            self.bidPriceMap[reqId].append(price)
            print("BID:", price)
