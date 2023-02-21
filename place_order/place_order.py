import logging
from ib_api_client.ib_api_client import IBApiClient
from ibapi.contract import Contract
from ibapi.order import Order

logger = logging.getLogger(__name__)


class PlaceOrder:
    def __init__(self, app: IBApiClient):
        self.app = app

    def execute_order(self, contract: Contract, order: Order):
        self.app.placeOrder(order.orderId, contract, order)

    def get_fx_order_contract(self, symbol, currency):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = 'CASH'
        contract.exchange = 'IDEALPRO'
        contract.currency = currency
        return contract

    def get_order(self, action: str, qty: int, order_type: str, limit_price = None):
        order = Order()
        order.orderId = self.app.nextorderId
        self.app.nextorderId += 1
        order.action = action
        order.totalQuantity = qty
        order.orderType = order_type
        if limit_price is not None and order_type == 'LMT':
            order.lmtPrice = limit_price
        return order
