from ib_api_client.ib_api_client import IBApiClient
from ibapi.common import MarketDataTypeEnum


class RequestMarketData:

    def __init__(self, app: IBApiClient, callbackFnMap):
        self.app = app
        self.callbackFnMap = callbackFnMap

    def request_market_data(self, reqID, contract, callbackFn):
        self.callbackFnMap[reqID]['mktData'] = callbackFn
        self.app.reqMktData(reqID, contract, '', False, False, [])

    