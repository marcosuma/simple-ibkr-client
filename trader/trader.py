from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract

from place_order.ibkr_place_order import IBKRPlaceOrder

import oandapyV20

from place_order.oanda_place_order import OANDAPlaceOrder


class Trader:

    def __init__(self, ibkr_client: IBApiClient, oanda_client: oandapyV20.API, callbackFnMap, budget: float, existing_positions: dict = None) -> None:
        self.callbackFnMap = callbackFnMap
        self.ibkr_client = ibkr_client
        self.budget = budget
        if existing_positions is not None:
            self.positions = existing_positions
        else:
            self.positions = {}
        self.contract_by_order_id = {}
        self.oanda_client = oanda_client
        self.is_oanda_long = False
        self.is_oanda_short = False

    def _ibkrOrderStatusFn(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice, order):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled',
              filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice, 'permId', permId, 'parentId', parentId, 'clientId', clientId, 'whyHeld', whyHeld, 'mktCapPrice', mktCapPrice, 'order', order)
        symbol = self.contract_by_order_id[orderId].symbol
        
        if remaining == 0:
            if order == "SELL":
                filled *= -1
            self.positions[symbol] = float(filled)
            self.budget -= float(avgFullPrice) * float(filled)

        print('positions:', self.positions)
        print('budget:', self.budget)

    def buy(self, contract: Contract, order_type: str, quantity: int, close_existing_positions: bool, limit_price=None, stop_loss=None, target_profit=None):
        if close_existing_positions and self.positionExists(contract.symbol) and self.isShort(contract.symbol):
            # close the existing position if it's a short
            quantity = -2 * self.getPositionQty(contract.symbol)
            print("closing short position in %s mode at price %s and qty %s" %
                  (order_type, limit_price, (quantity / 2)))
        elif quantity is None:
            # we maximize the quantity based on current budget
            if limit_price is None:
                raise ValueError(
                    "At least one between quantity and limit_price must be provided")
            quantity = self.budget // limit_price

        ########################### PLACE ORDER #################################
        ibkr_place_order = IBKRPlaceOrder(self.ibkr_client)
        order_id = ibkr_place_order.executeOrder(
            contract,
            ibkr_place_order.getOrder(action='BUY', qty=quantity,
                                      order_type=order_type, limit_price=limit_price)
        )
        self.callbackFnMap[order_id]['orderStatus'] = self._ibkrOrderStatusFn
        self.contract_by_order_id[order_id] = contract

        # TODO: max_loss should be setup in some risk management class
        if self.is_oanda_long:
            return
        max_loss = self.budget * 0.01
        oanda_place_order = OANDAPlaceOrder(self.oanda_client)
        oanda_place_order.executeOrder(
            order='BUY',
            symbol=contract.symbol + "_" + contract.currency,
            limit_price=limit_price,
            time_in_force='GTC',
            risk=max_loss,
            stop_loss=stop_loss,
            target_profit=target_profit
        )
        self.is_oanda_long = True
        self.is_oanda_short = False
        ########################### PLACE ORDER #################################

    def sell(self, contract: Contract, order_type: str, quantity: int, close_existing_positions: bool, limit_price=None, stop_loss=None, target_profit=None):
        if close_existing_positions and self.positionExists(contract.symbol) and self.isLong(contract.symbol):
            # close the existing position if it's a short
            quantity = 2 * self.getPositionQty(contract.symbol)
            print("closing long position in %s mode at price %s and qty %s" %
                  (order_type, limit_price, (quantity / 2)))
        elif quantity is None:
            # we maximize the quantity based on current budget
            if limit_price is None:
                raise ValueError(
                    "At least one between quantity and limit_price must be provided")
            quantity = self.budget // limit_price

        ########################### PLACE ORDER #################################
        place_order = IBKRPlaceOrder(self.ibkr_client)
        order_id = place_order.executeOrder(
            contract,
            place_order.getOrder(action='SELL', qty=quantity,
                                 order_type=order_type, limit_price=limit_price)
        )
        self.callbackFnMap[order_id]['orderStatus'] = self._ibkrOrderStatusFn
        self.contract_by_order_id[order_id] = contract

        # TODO: max_loss should be setup in some risk management class
        if self.is_oanda_short:
            return
        max_loss = self.budget * 0.001
        oanda_place_order = OANDAPlaceOrder(self.oanda_client)
        oanda_place_order.executeOrder(
            order='SELL',
            symbol=contract.symbol + "_" + contract.currency,
            limit_price=limit_price,
            time_in_force='GTC',
            risk=max_loss,
            stop_loss=stop_loss,
            target_profit=target_profit
        )
        self.is_oanda_short = True
        self.is_oanda_long = False
        ########################### PLACE ORDER #################################

    def positionExists(self, contract_symbol: str):
        return self.positions.get(contract_symbol) is not None

    def isLong(self, contract_symbol: str):
        return self.positions.get(contract_symbol, 0) > 0

    def isShort(self, contract_symbol: str):
        return self.positions.get(contract_symbol, 0) < 0

    def getPositionQty(self, contract_symbol: str):
        return self.positions.get(contract_symbol)
