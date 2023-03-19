#!/usr/bin/env python
# coding: utf-8

from svm_strategy.svm_strategy import SVMStrategy
from marsi_strategy.marsi_strategy import MARSIStrategy
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

from technical_indicators.technical_indicators import TechnicalIndicators
from machine_learning.svm_buy_predictor import SVMBuyPredictor

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

########################### REQUEST MARKED DATA #################################
    # app.reqMarketDataType(MarketDataTypeEnum.REALTIME)
    # app.reqMarketDataType(MarketDataTypeEnum.DELAYED)

    # id = 1000
    # contract = Contract()
    # contract.symbol = 'EUR'
    # contract.secType = 'CASH'
    # contract.exchange = 'IDEALPRO'
    # contract.currency = 'USD'

    # from request_market_data.request_market_data import RequestMarketData
    # from request_market_data.callback import Callback as RMDCallback
    # rmd_object = RequestMarketData(app, callbackFnMap)
    # rmd_cb = RMDCallback(askPriceMap, bidPriceMap)
    # rmd_object.request_market_data(
    #     enel_id, enel_contract, rmd_cb.handleMktDataEnel)
    # rmd_object.request_market_data(id, contract, , handleDataAlibaba)
    # request_market_data.request_markeczt_data(bitcoin_futures_id, bitcoin_futures_contract, handleDataBitcoinFutures)
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
    interval = '6 M'
    timePeriod = '4 hours'
    file_to_save = "data/data-{}-{}-{}-{}-{}-{}.csv".format(
        contract.symbol, contract.secType, contract.exchange, contract.currency, interval, timePeriod)
    technical_indicators = TechnicalIndicators(
        candlestickData, file_to_save)

    def combine_fn(reqId, start, end):
        df = technical_indicators.process_data(reqId, start, end)
        MARSIStrategy().execute(df)
        df, _ = SVMBuyPredictor(
            plotsQueue, file_to_save).process_data_with_file(df)
        # Plot(df, plotsQueue).plot()

    def combine_fn_file(df):
        df = technical_indicators.process_data_with_file(df)
        MARSIStrategy().execute(df)
        df, model = SVMBuyPredictor(
            plotsQueue, file_to_save).process_data_with_file(df)
        # Plot(df, plotsQueue).plot()

        # Request new historical data in "live" mode so that actions can be taken on the market
        # strategy = SVMStrategy(df, model, file_to_save, app, contract, 10_000)
        # rhd_object.request_historical_data(
        #     reqID=id+1, contract=contract, interval="1 D", timePeriod="5 mins", dataType='MIDPOINT', rth=0, timeFormat=2, keepUpToDate=True, atDatapointFn=lambda x, y: None, afterAllDataFn=lambda reqId, start, end: print("Do nothing", reqId, start, end), atDatapointUpdateFn=strategy.executeTrade)

    import os
    if not os.path.exists(file_to_save):
        rhd_object.request_historical_data(
            reqID=id, contract=contract, interval=interval, timePeriod=timePeriod, dataType='MIDPOINT', rth=0, timeFormat=2, keepUpToDate=False, atDatapointFn=rhd_cb.handle, afterAllDataFn=combine_fn, atDatapointUpdateFn=lambda x, y: None)
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
