from backtest_env.order import OrderType, Order
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet


class OrderManager:
    def __init__(self, position_manager: PositionManager, price_dataset: PriceDataSet):
        self.orders = {}
        self.filled_orders = []
        self.order_handlers = {OrderType.Market: self.handle_market_order}
        self.position_manager = position_manager
        self.price_dataset = price_dataset

    def get_all_orders(self) -> list[Order]:
        return list(self.orders.values())

    def get_order_history(self) -> list[Order]:
        return self.filled_orders

    def add_order(self, order: Order):
        self.orders[order.id] = order

    def add_orders(self, orders: list[Order]):
        for order in orders:
            self.add_order(order)

    def cancel_all_orders(self):
        self.orders = {}

    def get_orders_by_side(self, side: str) -> list[Order]:
        orders = filter(lambda order: order.side == side, self.orders.values())
        return sorted(orders, key=lambda x: x.created_at)

    def process_orders(self):
        for order in list(self.orders.values()):
            handler = self.order_handlers.get(order.type, self.handle_stop_order)  # handler is just a function
            handler(order)

    def handle_market_order(self, order: Order):
        self.position_manager.fill(order)
        self.filled_orders.append(order)
        del self.orders[order.id]

    def handle_stop_order(self, order):
        p = self.price_dataset.get_current_price()
        # if price is in the candle body then treats it as market order
        if p.low <= order.price <= p.high:
            self.handle_market_order(order)
