#!/usr/bin/env python
# coding: utf-8

import request_historical_data.request_historical_data as rhd
import request_historical_data.callback as rhd_callback
import pandas as pd
import machine_learning.ml_candlestick_predictor as ml_candlestick_predictor
import patterns.patterns as patterns
import time
from collections import defaultdict
from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import talib as ta

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


def printCandlestick(stock_df):
    candlestick = go.Candlestick(x=stock_df["Date"],
                                 open=stock_df["Open"],
                                 high=stock_df["High"],
                                 low=stock_df["Low"],
                                 close=stock_df["Close"])
    fig = go.Figure(data=[candlestick])
    fig.layout.xaxis.type = 'category'
    fig.show()


def marubozuCandles(stock_df):
    # Identify the marubozu candles in the dataset
    stock_df['marubozu'] = ta.CDLMARUBOZU(
        stock_df['Open'], stock_df['High'], stock_df['Low'], stock_df['Close'])
    # Subset dataframe for only the marubozu candles
    marubozu_candles = stock_df[stock_df['marubozu'] != 0]

    # display(marubozu_candles[['Close', 'marubozu']])
    printCandlestick(marubozu_candles)


def pivotid(df1, l, n1, n2):  # n1 n2 before and after candle l
    if l-n1 < 0 or l+n2 >= len(df1):
        return 0

    pividlow = 1
    pividhigh = 1
    for i in range(l-n1, l+n2+1):
        if df1.low[l] > df1.low[i]:
            pividlow = 0
        if df1.high[l] < df1.high[i]:
            pividhigh = 0

    if pividlow and pividhigh:
        return 3
    elif pividlow:
        return 1
    elif pividhigh:
        return 2
    else:
        return 0


def pointpos(x):
    if x['pivot'] == 1:
        return float(x['low']) - 1e-5
    elif x['pivot'] == 2:
        return float(x['high']) + 1e-5
    else:
        return np.nan


def check_if_triangle(candleid, backcandles, df):
    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    for i in range(candleid - backcandles, candleid + 1):
        if df.iloc[i].pivot == 1:
            minim = np.append(minim, float(df.iloc[i].low))
            xxmin = np.append(xxmin, i)
        if df.iloc[i].pivot == 2:
            maxim = np.append(maxim, float(df.iloc[i].high))
            xxmax = np.append(xxmax, i)

    if (xxmax.size < 5 and xxmin.size < 5) or xxmax.size == 0 or xxmin.size == 0:
        raise ValueError(
            "no triangle found - ((xxmax.size < 3 and xxmin.size < 3) or xxmax.size == 0 or xxmin.size == 0)")

    slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
    slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)

    # # and slmax <= -0.01:
    # if abs(rmax) >= 0.4 and abs(rmin) >= 0.4:  # and abs(slmin) <= 0.001:
    #     print(rmin, rmax, candleid)
    #     return slmin, intercmin, slmax, intercmax, xxmin, xxmax

    if (slmin >= 0 and slmax < 0) or (slmin > 0 and slmax <= 0):
        print(rmin, rmax, candleid)
        return slmin, intercmin, slmax, intercmax, xxmin, xxmax

    if candleid % 1000 == 0:
        print(candleid)

    raise ValueError("no triangle found")


def afterAllData2(reqId: int, start: str, end: str):
    df = pd.DataFrame(data=np.array(candlestickData), columns=[
        "date", "open", "close", "high", "low", "volume"])

    df.reset_index(drop=True, inplace=True)
    df.isna().sum()

    df['pivot'] = df.apply(lambda x: pivotid(df, x.name, 3, 3), axis=1)
    df['pointpos'] = df.apply(lambda row: pointpos(row), axis=1)

    backcandles = 100
    dfpl = df

    fig = go.Figure(data=[go.Candlestick(x=dfpl.index, open=dfpl['open'],
                    high=dfpl['high'], low=dfpl['low'], close=dfpl['close'])])

    fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers", marker=dict(
        size=4, color="MediumPurple"), name="pivot")

    candleid = backcandles
    while candleid < len(dfpl) - 1:
        try:
            slmin, intercmin, slmax, intercmax, xxmin, xxmax = check_if_triangle(
                candleid, backcandles, df)
            fig.add_trace(go.Scatter(x=xxmin, y=slmin*xxmin +
                                     intercmin, mode='lines', name='min slope'))
            fig.add_trace(go.Scatter(x=xxmax, y=slmax*xxmax +
                                     intercmax, mode='lines', name='max slope'))
            fig.update_layout(xaxis_rangeslider_visible=False)
            candleid += int(backcandles * 0.5)
        except ValueError as err:
            print(err)
            candleid += 1
            continue

    fig.show()

    # def plotFn():
    #     dfpl = df
    #     fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
    #                                          open=pd.to_numeric(dfpl['open']),
    #                                          close=pd.to_numeric(
    #                                              dfpl['close']),
    #                                          high=pd.to_numeric(dfpl['high']),
    #                                          low=pd.to_numeric(dfpl['low']))])

    #     fig.add_scatter(x=dfpl.index, y=dfpl['pointpos'], mode="markers", marker=dict(
    #         size=5, color="MediumPurple"), name="pivot")

    #     fig.show()

    # plotsQueue.append(plotFn)


# def afterAllData(reqId: int, start: str, end: str):


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
    file_to_save = "data-{}-{}-{}-{}.csv".format(
        contract.symbol, contract.secType, contract.exchange, contract.currency)
    # ml_processor = ml.MachineLearning(candlestickData, plotsQueue)
    # ml_processor = ml_candlestick_predictor.MLCandlestickPredictor(
    #     candlestickData, plotsQueue, file_to_save)
    processor = patterns.Patterns(candlestickData, plotsQueue, file_to_save)

    import os
    if not os.path.exists(file_to_save):
        rhd_object.request_historical_data(
            reqID=gld_id, contract=contract, interval='1 Y', timePeriod='1 hour', dataType='BID', rth=0, timeFormat=2, atDatapointFn=rhd_cb.handleEnel, afterAllDataFn=processor.process_data)
    else:
        print('File already exists. Loading data from CSV')
        df = pd.read_csv(file_to_save)
        processor.process_data_with_file(df)


########################### REQUEST HISTORICAL DATA #################################

########################### SAVE HISTORICAL DATA USING PANDAS ###################################
# time.sleep(5)
# df = pd.DataFrame(priceByTime.values(), columns=['DateTime', 'Close'])
# df['DateTime'] = pd.to_datetime(df['DateTime'], unit='s')
# df.to_csv('Enel.csv')
########################### SAVE HISTORICAL DATA USING PANDAS ###################################


# from ibapi.client import EClient
# from ibapi.wrapper import EWrapper
# from ibapi.contract import Contract
# from ibapi.order import *

# import threading
# import time

# class IBapi(EWrapper, EClient):

# 	def __init__(self):
# 		EClient.__init__(self, self)

# 	def nextValidId(self, orderId: int):
# 		super().nextValidId(orderId)
# 		self.nextorderId = orderId
# 		print('The next valid order id is: ', self.nextorderId)

# 	def orderStatus(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
# 		print('orderStatus - orderid:', orderId, 'status:', status, 'filled', filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)

# 	def openOrder(self, orderId, contract, order, orderState):
# 		print('openOrder id:', orderId, contract.symbol, contract.secType, '@', contract.exchange, ':', order.action, order.orderType, order.totalQuantity, orderState.status)

# 	def execDetails(self, reqId, contract, execution):
# 		print('Order Executed: ', reqId, contract.symbol, contract.secType, contract.currency, execution.execId, execution.orderId, execution.shares, execution.lastLiquidity)


# def run_loop():
# 	app.run()

# def FX_order(symbol):
# 	contract = Contract()
# 	contract.symbol = symbol[:3]
# 	contract.secType = 'CASH'
# 	contract.exchange = 'IDEALPRO'
# 	contract.currency = symbol[3:]
# 	return contract

# app = IBapi()
# app.connect('127.0.0.1', 7497, 123)

# app.nextorderId = None

# #Start the socket in a thread
# api_thread = threading.Thread(target=run_loop, daemon=True)
# api_thread.start()

# #Check if the API is connected via orderid
# while True:
# 	if isinstance(app.nextorderId, int):
# 		print('connected')
# 		print()
# 		break
# 	else:
# 		print('waiting for connection')
# 		time.sleep(1)

# #Create order object
# order = Order()
# order.action = 'BUY'
# order.totalQuantity = 100000
# order.orderType = 'MKT'
# # order.lmtPrice = '1.10'
# order.orderId = app.nextorderId
# app.nextorderId += 1
# order.transmit = False

# #Create stop loss order object
# stop_order = Order()
# stop_order.action = 'SELL'
# stop_order.totalQuantity = 100000
# stop_order.orderType = 'STP'
# stop_order.auxPrice = '1.09'
# stop_order.orderId = app.nextorderId
# app.nextorderId += 1
# stop_order.parentId = order.orderId
# order.transmit = True

# #Place orders
# app.placeOrder(order.orderId, FX_order('EURUSD'), order)
# app.placeOrder(stop_order.orderId, FX_order('EURUSD'), stop_order)

# app.disconnect()

    while True:
        # manage plots
        if len(plotsQueue) > 0:
            seriesFn = plotsQueue.pop()
            seriesFn()
        else:
            time.sleep(2)
