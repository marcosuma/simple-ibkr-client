#!/usr/bin/env python
# coding: utf-8

import request_historical_data.request_historical_data as rhd
import request_historical_data.callback as rhd_callback
import pandas as pd
import time
from collections import defaultdict
from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract
import matplotlib.pyplot as plt

import threading
import collections

# matplotlib.use("MacOSX")
plt.style.use('fivethirtyeight')


def run_loop():
    app.run()


askPriceMap = defaultdict(lambda: [])
bidPriceMap = defaultdict(lambda: [])
candlestickData = []
plotsQueue = collections.deque([])

if __name__ == "__main__":

    callbackFnMap = defaultdict(lambda: defaultdict(lambda: None))
    app = IBApiClient(callbackFnMap)
    app.connect('127.0.0.1', 7497, 123)

    # Start the socket in a thread
    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # time.sleep(1)  # Sleep interval to allow time for connection to server

    while True:
        if isinstance(app.nextorderId, int):
            print("connected")
            break
        else:
            print("Waiting for connection to server")
            time.sleep(1)

########################### PLACE ORDER #################################
    # place_order = PlaceOrder(app)
    # place_order.execute_order(
    #     place_order.get_fx_order_contract(symbol="USD", currency="SGD"),
    #     place_order.get_order(action='SELL', qty=10000,
    #                           order_type='MKT')
    # )
########################### PLACE ORDER #################################

########################### REQUEST MARKED DATA #################################
# app.reqMarketDataType(MarketDataTypeEnum.REALTIME)
# app.reqMarketDataType(MarketDataTypeEnum.DELAYED)

# bitcoin_futures_id = 1000
# bitcoin_futures_contract = Contract()
# bitcoin_futures_contract.symbol = 'BRR'
# bitcoin_futures_contract.secType = 'FUT'
# bitcoin_futures_contract.exchange = 'CME'
# bitcoin_futures_contract.lastTradeDateOrContractMonth = '202303'

# enel_id = 1001
# enel_contract = Contract()
# enel_contract.symbol = 'ENEL'
# enel_contract.secType = 'STK'
# enel_contract.exchange = 'BVME'
# enel_contract.currency = 'EUR'

# eur_usd_id = 1002
# eur_usd_contract = Contract()
# eur_usd_contract.symbol = 'EUR'
# eur_usd_contract.secType = 'CASH'
# eur_usd_contract.exchange = 'IDEALPRO'
# eur_usd_contract.currency = 'USD'

# rmd_object = rmd.RequestMarketData(app, callbackFnMap)
# rmd_cb = rmd_callback.Callback(askPriceMap, bidPriceMap)
# rmd_object.request_market_data(
#     enel_id, enel_contract, rmd_cb.handleMktDataEnel)
# request_market_data.request_market_data(id, contract, , handleDataAlibaba)
# request_market_data.request_market_data(bitcoin_futures_id, bitcoin_futures_contract, handleDataBitcoinFutures)
# request_market_data.request_market_data(eur_usd_id, eur_usd_contract, handleDataEurUsd)
########################### REQUEST MARKED DATA #################################

########################### REQUEST HISTORICAL DATA #################################
    gld_id = 1000
    contract = Contract()
    contract.symbol = 'ETH'
    contract.secType = 'CRYPTO'
    contract.exchange = 'PAXOS'
    contract.currency = 'USD'
    rhd_object = rhd.RequestHistoricalData(app, callbackFnMap)
    rhd_cb = rhd_callback.Callback(candlestickData)
    interval = '1 M'
    timePeriod = '1 hour'
    file_to_save = "data-{}-{}-{}-{}-{}-{}.csv".format(
        contract.symbol, contract.secType, contract.exchange, contract.currency, interval, timePeriod)
    # ml_processor = ml.MachineLearning(candlestickData, plotsQueue)
    # ml_processor = ml_candlestick_predictor.MLCandlestickPredictor(
    #     candlestickData, plotsQueue, file_to_save)
    from technical_indicators.technical_indicators import TechnicalIndicators
    processor = TechnicalIndicators(candlestickData, plotsQueue, file_to_save)

    import os
    if not os.path.exists(file_to_save):
        rhd_object.request_historical_data(
            reqID=gld_id, contract=contract, interval=interval, timePeriod=timePeriod, dataType='BID', rth=0, timeFormat=2, atDatapointFn=rhd_cb.handle, afterAllDataFn=processor.process_data)
    else:
        print('File already exists. Loading data from CSV')
        df = pd.read_csv(file_to_save)
        processor.process_data_with_file(df)


########################### REQUEST HISTORICAL DATA #################################

    while True:
        # manage plots
        if len(plotsQueue) > 0:
            seriesFn = plotsQueue.pop()
            seriesFn()
        else:
            time.sleep(2)
