import oandapyV20
import math
import oandapyV20.endpoints.orders as orders
import os


class OANDAPlaceOrder(object):
    def __init__(self, oanda_client: oandapyV20.API):
        self.oanda_client = oanda_client

    def executeOrder(self, order, symbol, limit_price, time_in_force, risk, stop_loss, target_profit, gtd_time: None):
        units = math.floor(risk / abs(limit_price - stop_loss))
        if order == 'SELL':
            units *= -1
        data = {
            "order": {
                "instrument": symbol,
                "price": '%.4f'%(round(limit_price, 4)),
                "stopLossOnFill": {
                    "timeInForce": 'GTC',
                    "price": '%.4f'%(round(stop_loss, 4))
                },
                "takeProfitOnFill": {
                    "timeInForce": 'GTC',
                    "price": '%.4f'%(round(target_profit, 4))
                },
                "timeInForce": time_in_force,
                "gtdTime": gtd_time,
                "units": units,
                "type": "STOP",
                "positionFill": "DEFAULT"
            }
        }
        print('submitting order to Oanda with data:', data)
        r = orders.OrderCreate(os.environ.get('OANDA_ACCOUNT_ID'), data=data)
        self.oanda_client.request(r)
        print(r.response)
