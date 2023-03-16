import logging
from ibapi.client import EClient
from ibapi.ticktype import TickTypeEnum
from ibapi.wrapper import EWrapper

logger = logging.getLogger(__name__)


class IBApiClient(EWrapper, EClient):
    def __init__(self, callbackFnMap):
        EClient.__init__(self, self)
        self.callbackFnMap = callbackFnMap
        self.nextorderId = None

    def tickPrice(self, reqId, tickType, price, attrib):
        self.callbackFnMap[reqId]['mktData'](reqId, tickType, price, attrib)

    def historicalData(self, reqId, bar):
        self.callbackFnMap[reqId]['historicalData'](reqId, bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        self.callbackFnMap[reqId]['historicalDataEnd'](reqId, start, end)

    def historicalDataUpdate(self, reqId, bar):
        self.callbackFnMap[reqId]['historicalDataUpdate'](reqId, bar)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print('The next valid order id is: ', self.nextorderId)

    def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled',
              filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

    def openOrder(self, orderId, contract, order, orderState):
        print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange,
              ':', order.action, order.orderType, order.totalQuantity, orderState.status)

    def execDetails(self, reqId, contract, execution):
        print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency,
              execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson):
        print(reqId, errorCode, errorString, advancedOrderRejectJson)
        # if errorCode == 202:
        #     print('order canceled')
