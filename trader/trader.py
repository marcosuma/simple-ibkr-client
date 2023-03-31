from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract

from place_order.ibkr_place_order import IBKRPlaceOrder

import oandapyV20

from place_order.oanda_place_order import OANDAPlaceOrder


class Trader:

    def __init__(self, ibkr_client: IBApiClient, oanda_client: oandapyV20.API, budget: float, callbackFnMap, oanda_positions: list, oanda_account_summary: list) -> None:
        self.callbackFnMap = callbackFnMap
        self.ibkr_client = ibkr_client
        self.budget = budget
        self.positions = {}
        self.oanda_positions = oanda_positions
        self.oanda_account_summary = oanda_account_summary
        self.contract_by_order_id = {}
        self.oanda_client = oanda_client

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
        # ########################### IBKR PLACE ORDER #################################
        # if close_existing_positions and self.positionExists(contract.symbol) and self.isShort(contract.symbol):
        #     # close the existing position if it's a short
        #     quantity = -2 * self.getPositionQty(contract.symbol)
        #     print("closing short position in %s mode at price %s and qty %s" %
        #           (order_type, limit_price, (quantity / 2)))
        # elif quantity is None:
        #     # we maximize the quantity based on current budget
        #     if limit_price is None:
        #         raise ValueError(
        #             "At least one between quantity and limit_price must be provided")
        #     quantity = self.budget // limit_price

        # ibkr_place_order = IBKRPlaceOrder(self.ibkr_client)
        # order_id = ibkr_place_order.executeOrder(
        #     contract,
        #     ibkr_place_order.getOrder(action='BUY', qty=quantity,
        #                               order_type=order_type, limit_price=limit_price)
        # )
        # self.callbackFnMap[order_id]['orderStatus'] = self._ibkrOrderStatusFn
        # self.contract_by_order_id[order_id] = contract
        # ########################### END PLACE ORDER #################################

        ########################### OANDA PLACE ORDER #################################
        instrument = contract.symbol + "_" + contract.currency

        instrument_position = self.oanda_positions[0][instrument]
        if instrument_position is not None:
            long = instrument_position['long']
            short = instrument_position['short']
            if long['units'] != 0:
                print("LONG POSITION ALREADY EXIST. PASS THIS ONE")
                return
            if short['units'] != 0:
                print("THERE IS AN EXISTING SHORT POSITION. NEED TO CLOSE THIS ONE")
                import oandapyV20.endpoints.positions as positions
                import os
                data = {
                    "shortUnits": "ALL"
                }
                r = positions.PositionClose(accountID=os.environ.get('OANDA_ACCOUNT_ID'),
                                             instrument=instrument,
                                             data=data)
                self.oanda_client.request(r)

        # TODO: max_loss should be setup in some risk management class
        max_loss = 100
        oanda_place_order = OANDAPlaceOrder(self.oanda_client)
        oanda_place_order.executeOrder(
            order='BUY',
            symbol=instrument,
            limit_price=limit_price,
            time_in_force='GTC',
            risk=max_loss,
            stop_loss=stop_loss,
            target_profit=target_profit
        )
        ########################### END PLACE ORDER #################################

    def sell(self, contract: Contract, order_type: str, quantity: int, close_existing_positions: bool, limit_price=None, stop_loss=None, target_profit=None):
        # ########################### IBKR PLACE ORDER #################################
        # if close_existing_positions and self.positionExists(contract.symbol) and self.isLong(contract.symbol):
        #     # close the existing position if it's a short
        #     quantity = 2 * self.getPositionQty(contract.symbol)
        #     print("closing long position in %s mode at price %s and qty %s" %
        #           (order_type, limit_price, (quantity / 2)))
        # elif quantity is None:
        #     # we maximize the quantity based on current budget
        #     if limit_price is None:
        #         raise ValueError(
        #             "At least one between quantity and limit_price must be provided")
        #     quantity = self.budget // limit_price

        # place_order = IBKRPlaceOrder(self.ibkr_client)
        # order_id = place_order.executeOrder(
        #     contract,
        #     place_order.getOrder(action='SELL', qty=quantity,
        #                          order_type=order_type, limit_price=limit_price)
        # )
        # self.callbackFnMap[order_id]['orderStatus'] = self._ibkrOrderStatusFn
        # self.contract_by_order_id[order_id] = contract
        # ########################### END PLACE ORDER #################################

        ########################### OANDA PLACE ORDER #################################
        instrument = contract.symbol + "_" + contract.currency
        instrument_position = self.oanda_positions[0][instrument]
        if instrument_position is not None:
            long = instrument_position['long']
            short = instrument_position['short']
            if short['units'] != 0:
                print("SHORT POSITION ALREADY EXIST. PASS THIS ONE")
                return
            if long['units'] != 0:
                print("THERE IS AN EXISTING LONG POSITION. NEED TO CLOSE THIS ONE")
                import oandapyV20.endpoints.positions as positions
                import os
                data = {
                    "longUnits": "ALL"
                }
                r = positions.PositionClose(accountID=os.environ.get('OANDA_ACCOUNT_ID'),
                                             instrument=instrument,
                                             data=data)
                self.oanda_client.request(r)
        # TODO: max_loss should be setup in some risk management class
        max_loss = 100
        oanda_place_order = OANDAPlaceOrder(self.oanda_client)
        oanda_place_order.executeOrder(
            order='SELL',
            symbol=instrument,
            limit_price=limit_price,
            time_in_force='GTC',
            risk=max_loss,
            stop_loss=stop_loss,
            target_profit=target_profit
        )
        ########################### END PLACE ORDER #################################

    def positionExists(self, contract_symbol: str):
        return self.positions.get(contract_symbol) is not None

    def isLong(self, contract_symbol: str):
        return self.positions.get(contract_symbol, 0) > 0

    def isShort(self, contract_symbol: str):
        return self.positions.get(contract_symbol, 0) < 0

    def getPositionQty(self, contract_symbol: str):
        return self.positions.get(contract_symbol)
