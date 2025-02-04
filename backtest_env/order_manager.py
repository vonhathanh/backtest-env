from backtest_env.order import OrderType, Order
from backtest_env.position_manager import PositionManager


class OrderManager:
    def __init__(self, position_mgr: PositionManager):
        self.orders = {}
        self.order_handlers = {
            OrderType.Market: self.handle_market_order,
            OrderType.Limit: self.handle_limit_order,
            OrderType.TakeProfit: self.handle_limit_order,
            OrderType.Stoploss: self.handle_limit_order,
        }
        self.position_mgr = position_mgr

    def get_orders(self):
        return list(self.orders.values())

    def add_order(self, order: Order):
        self.orders[order.id] = order

    def add_orders(self, orders: list[Order]):
        [self.add_order(order) for order in orders]

    def cancel_all_orders(self):
        self.orders = {}

    def process_orders(self):
        for order_id in list(self.orders.keys()):
            order = self.orders[order_id]
            handler = self.order_handlers[order.type]
            handler(order)
            del self.orders[order_id]

    def handle_market_order(self, order: Order):
        print("handler called", order)
        # self.position_mgr.fill(order)


    def handle_limit_order(self, order):
        self.handle_stop_order(order)

    def handle_stop_order(self, order):
        pass
        # p = self.prices.get_current_price()
        # # move from high to low to check if the order price is in this range
        # # high > order price which means order can be filled
        # if order.price <= p.high and order.side == "BUY":
        #     self.handle_market_order(order)
        # # low < order price which means order can be filled
        # if order.price >= p.low and order.side == "SELL":
        #     self.handle_market_order(order)