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
    # processor = patterns.Patterns(candlestickData, plotsQueue, file_to_save)
    import triangles.triangles as triangles
    processor = triangles.Triangles(candlestickData, plotsQueue, file_to_save)

    import os
    if not os.path.exists(file_to_save):
        rhd_object.request_historical_data(
            reqID=gld_id, contract=contract, interval=interval, timePeriod=timePeriod, dataType='BID', rth=0, timeFormat=2, atDatapointFn=rhd_cb.handle, afterAllDataFn=processor.process_data)
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
