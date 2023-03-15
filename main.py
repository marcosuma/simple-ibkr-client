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
from strategy.marsi_strategy import MARSIStrategy

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

# rmd_object = rmd.RequestMarketData(app, callbackFnMap)
# rmd_cb = rmd_callback.Callback(askPriceMap, bidPriceMap)
# rmd_object.request_market_data(
#     enel_id, enel_contract, rmd_cb.handleMktDataEnel)
# request_market_data.request_market_data(id, contract, , handleDataAlibaba)
# request_market_data.request_market_data(bitcoin_futures_id, bitcoin_futures_contract, handleDataBitcoinFutures)
# request_market_data.request_market_data(eur_usd_id, eur_usd_contract, handleDataEurUsd)
########################### REQUEST MARKED DATA #################################

########################### REQUEST HISTORICAL DATA #################################
    id = 1000
    contract = Contract()
    contract.symbol = 'ETH'
    contract.secType = 'CRYPTO'
    contract.exchange = 'PAXOS'
    contract.currency = 'USD'
    rhd_object = rhd.RequestHistoricalData(app, callbackFnMap)
    rhd_cb = rhd_callback.Callback(candlestickData)
    interval = '1 Y'
    timePeriod = '1 hour'
    file_to_save = "data/data-{}-{}-{}-{}-{}-{}.csv".format(
        contract.symbol, contract.secType, contract.exchange, contract.currency, interval, timePeriod)
    from technical_indicators.technical_indicators import TechnicalIndicators
    from machine_learning.svm_buy_predictor import SVMBuyPredictor
    from plot.plot import Plot
    technical_indicators = TechnicalIndicators(
        candlestickData, plotsQueue, file_to_save)

    def combine_fn(reqId, start, end):
        df = technical_indicators.process_data(reqId, start, end)
        MARSIStrategy().execute(df)
        df, _ = SVMBuyPredictor(
            plotsQueue, file_to_save).process_data_with_file(df)
        Plot(df, plotsQueue).plot()

    def combine_fn_file(df):
        df = technical_indicators.process_data_with_file(df)
        MARSIStrategy().execute(df)
        df, _ = SVMBuyPredictor(
            plotsQueue, file_to_save).process_data_with_file(df)
        Plot(df, plotsQueue).plot()

    import os
    if not os.path.exists(file_to_save):
        rhd_object.request_historical_data(
            reqID=id, contract=contract, interval=interval, timePeriod=timePeriod, dataType='MIDPOINT', rth=0, timeFormat=2, atDatapointFn=rhd_cb.handle, afterAllDataFn=combine_fn)
    else:
        print('File already exists. Loading data from CSV')
        df = pd.read_csv(file_to_save)
        combine_fn_file(df)


########################### REQUEST HISTORICAL DATA #################################

    while True:
        # manage plots
        if len(plotsQueue) > 0:
            seriesFn = plotsQueue.pop()
            seriesFn()
        else:
            time.sleep(2)
