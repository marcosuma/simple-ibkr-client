from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract

from place_order.place_order import PlaceOrder


class IBKRTrader:

    def __init__(self, client: IBApiClient, callbackFnMap, budget: float, existing_positions: dict = None) -> None:
        self.callbackFnMap = callbackFnMap
        self.client = client
        self.budget = budget
        if existing_positions is not None:
            self.positions = existing_positions
        else:
            self.positions = {}
        self.contract_by_order_id = {}

    def _ibkrOrderStatusFn(self, orderId, status, filled, remaining, avgFullPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        print('orderStatus - orderid:', orderId, 'status:', status, 'filled',
              filled, 'remaining', remaining, 'lastFillPrice', lastFillPrice)
        symbol = self.contract_by_order_id[orderId].symbol
        # TODO: fill positions here...
        # TODO: then update budget...
        if remaining == 0:
            self.positions[symbol] = filled
            self.budget -= avgFullPrice * filled

    def buy(self, contract: Contract, order_type: str, quantity: int, close_existing_positions: bool, limit_price=None, stop_loss=None, target_profit=None):
        if close_existing_positions and self.positionExists(contract.symbol) and self.isShort(contract.symbol):
            # close the existing position if it's a short
            quantity = -2 * self.getPositionQty(contract.symbol)
            print("closing short position in %s mode at price %s and qty %s" % order_type %
                  limit_price % quantity / 2)
        elif quantity is None:
            # we maximize the quantity based on current budget
            if limit_price is None:
                raise ValueError(
                    "At least one between quantity and limit_price must be provided")
            quantity = self.budget // limit_price

        ########################### PLACE ORDER #################################
        place_order = PlaceOrder(self.client, self.callbackFnMap)
        order_id = place_order.execute_order(
            self.contract,
            place_order.get_order(action='BUY', qty=quantity,
                                  order_type=order_type, limit_price=limit_price)
        )
        self.callbackFnMap[order_id]['orderStatus'] = self.ibkrOrderStatusFn
        self.contract_by_order_id[order_id] = contract
        ########################### PLACE ORDER #################################

    def sell(self, contract: Contract, order_type: str, quantity: int, close_existing_positions: bool, limit_price=None, stop_loss=None, target_profit=None):
        if close_existing_positions and self.positionExists(contract.symbol) and self.isLong(contract.symbol):
            # close the existing position if it's a short
            quantity = 2 * self.getPositionQty(contract.symbol)
            print("closing long position in %s mode at price %s and qty %s" % order_type %
                  limit_price % quantity / 2)
        elif quantity is None:
            # we maximize the quantity based on current budget
            if limit_price is None:
                raise ValueError(
                    "At least one between quantity and limit_price must be provided")
            quantity = self.budget // limit_price

        ########################### PLACE ORDER #################################
        place_order = PlaceOrder(self.client, self.callbackFnMap)
        order_id = place_order.execute_order(
            self.contract,
            place_order.get_order(action='SELL', qty=quantity,
                                  order_type=order_type, limit_price=limit_price)
        )
        self.callbackFnMap[order_id]['orderStatus'] = self.ibkrOrderStatusFn
        self.contract_by_order_id[order_id] = contract
        ########################### PLACE ORDER #################################

    def positionExists(self, contract_symbol: str):
        return self.positions.get(contract_symbol) is not None

    def isLong(self, contract_symbol: str):
        return self.positions.get(contract_symbol) > 0

    def isShort(self, contract_symbol: str):
        return self.positions.get(contract_symbol) < 0

    def getPositionQty(self, contract_symbol: str):
        return self.positions.get(contract_symbol)
