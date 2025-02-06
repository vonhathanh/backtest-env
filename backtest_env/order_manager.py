from backtest_env.order import OrderType, Order
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceData


class OrderManager:
    def __init__(self, position_mgr: PositionManager, data: PriceData):
        self.orders = {}
        self.order_handlers = {
            OrderType.Market: self.handle_market_order,
            OrderType.Limit: self.handle_limit_order,
            OrderType.TakeProfit: self.handle_limit_order,
            OrderType.Stoploss: self.handle_limit_order,
        }
        self.position_mgr = position_mgr
        self.data = data

    def get_orders(self):
        return list(self.orders.values())

    def add_order(self, order: Order):
        self.orders[order.id] = order

    def add_orders(self, orders: list[Order]):
        [self.add_order(order) for order in orders]

    def cancel_all_orders(self):
        self.orders = {}

    def split_orders_by_side(self):
        long_orders, short_orders = [], []
        for order in self.orders.values():
            long_orders.append(order) if order.side == "BUY" else short_orders.append(order)
        return long_orders, short_orders

    def process_orders(self):
        for order_id in list(self.orders.keys()):
            order = self.orders[order_id]
            handler = self.order_handlers[order.type] # handler is just a function
            handler(order)
            del self.orders[order_id]

    def handle_market_order(self, order: Order):
        self.position_mgr.fill(order)

    def handle_limit_order(self, order):
        self.handle_stop_order(order)

    def handle_stop_order(self, order):
        p = self.data.get_current_price()
        # if price is in the candle body then treats it as market order
        if p.low <= order.price <= p.high:
            self.handle_market_order(order)