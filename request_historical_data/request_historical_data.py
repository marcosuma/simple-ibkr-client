from ibapi.common import MarketDataTypeEnum
from ib_api_client.ib_api_client import IBApiClient


class RequestHistoricalData:
    def __init__(self, app: IBApiClient, callbackFnMap, contextMap):
        self.app = app
        self.callbackFnMap = callbackFnMap
        self.contextMap = contextMap

    def request_historical_data(
        self,
        reqID,
        contract,
        interval,
        timePeriod,
        dataType,
        rth,
        timeFormat,
        keepUpToDate,
        atDatapointFn,
        afterAllDataFn,
        atDatapointUpdateFn,
        technicalIndicators,
        fileToSave,
        candlestickData
    ):
        self.callbackFnMap[reqID]["historicalData"] = atDatapointFn
        self.callbackFnMap[reqID]["historicalDataEnd"] = afterAllDataFn
        self.callbackFnMap[reqID]["historicalDataUpdate"] = atDatapointUpdateFn
        self.contextMap[reqID]["technicalIndicators"] = technicalIndicators
        self.contextMap[reqID]["fileToSave"] = fileToSave
        self.contextMap[reqID]["contract"] = contract
        self.contextMap[reqID]["candlestickData"] = candlestickData
        # https://interactivebrokers.github.io/tws-api/historical_bars.html
        self.app.reqHistoricalData(
            reqID,
            contract,
            "",
            interval,
            timePeriod,
            dataType,
            rth,
            timeFormat,
            keepUpToDate,
            [],
        )
