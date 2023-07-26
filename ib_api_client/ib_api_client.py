import logging
from ibapi.client import EClient
from ibapi.ticktype import TickTypeEnum
from ibapi.wrapper import EWrapper
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class IBApiClient(EWrapper, EClient):
    def __init__(self, callbackFnMap, contextMap):
        EClient.__init__(self, self)
        self.callbackFnMap = callbackFnMap
        self.contextMap = contextMap
        self.nextorderId = None
        self.orderTypeById = {}

    def tickPrice(self, reqId, tickType, price, attrib):
        self.callbackFnMap[reqId]["mktData"](reqId, tickType, price, attrib)

    def historicalData(self, reqId, bar):
        self.callbackFnMap[reqId]["historicalData"](reqId, bar)

    def historicalDataEnd(self, reqId: int, start: str, end: str):
        candlestick_data = self.contextMap[reqId]["candlestickData"]
        file_to_save = self.contextMap[reqId]["fileToSave"]
        df = pd.DataFrame(
            data=np.array(candlestick_data),
            columns=["date", "open", "close", "high", "low", "volume"],
        )
        df["date"] = df["date"].astype(int)
        df["close"] = df["close"].astype(float)
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df.to_csv(file_to_save)

        technical_indicators = self.contextMap[reqId]["technicalIndicators"]
        self.callbackFnMap[reqId]["historicalDataEnd"](df, technical_indicators, file_to_save, self.contextMap[reqId]["contract"])

    def historicalDataUpdate(self, reqId, bar):
        self.callbackFnMap[reqId]["historicalDataUpdate"](reqId, bar)

    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid order id is: ", self.nextorderId)

    def orderStatus(
        self,
        orderId,
        status,
        filled,
        remaining,
        avgFullPrice,
        permId,
        parentId,
        lastFillPrice,
        clientId,
        whyHeld,
        mktCapPrice,
    ):
        if self.callbackFnMap[orderId]["orderStatus"] is not None:
            self.callbackFnMap[orderId]["orderStatus"](
                orderId,
                status,
                filled,
                remaining,
                avgFullPrice,
                permId,
                parentId,
                lastFillPrice,
                clientId,
                whyHeld,
                mktCapPrice,
                self.orderTypeById[orderId],
            )

    def openOrder(self, orderId, contract, order, orderState):
        print(
            "openOrder id:",
            orderId,
            contract.symbol,
            contract.secType,
            "@",
            contract.exchange,
            ":",
            order.action,
            order.orderType,
            order.totalQuantity,
            orderState.status,
        )
        self.orderTypeById[orderId] = order

    def execDetails(self, reqId, contract, execution):
        print(
            "Order Executed: ",
            reqId,
            contract.symbol,
            contract.secType,
            contract.currency,
            execution.execId,
            execution.orderId,
            execution.shares,
            execution.lastLiquidity,
        )

    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=''):
        print(reqId, errorCode, errorString, advancedOrderRejectJson)
        # if errorCode == 202:
        #     print('order canceled')
