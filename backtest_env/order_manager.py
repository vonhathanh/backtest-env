from socketio import Client

from backtest_env.base_class.event_emitter import EventEmitter
from backtest_env.constants import LONG, SHORT, SELL, BUY
from backtest_env.order import OrderType, Order
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet, Price


class OrderManager(EventEmitter):
    def __init__(
        self,
        position_manager: PositionManager,
        price_dataset: PriceDataSet,
        sio: Client = None,
    ):
        super().__init__(sio)
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
        self.emit("new_orders", [order.json()])

    def add_orders(self, orders: list[Order]):
        for order in orders:
            # we don't call self.add_order() because want to trigger the new_orders event in bulk
            self.orders[order.id] = order
        self.emit("new_orders", [order.json() for order in orders])

    def cancel_all_orders(self):
        self.orders = {}
        self.emit("current_orders", [])

    def process_filled_order(self, order: Order):
        self.filled_orders.append(order)
        self.emit("order_filled", order.json())

    def close_all_positions(self, price: Price):
        [long, short] = self.position_manager.get_positions()
        if long.is_active():
            self.close_position(LONG, long.quantity, price)
        if short.is_active():
            self.close_position(SHORT, short.quantity, price)

    def close_position(self, position_side: str, quantity: float, price: Price):
        side = SELL if position_side == LONG else BUY
        order = Order(
            OrderType.Market,
            side,
            quantity,
            "",
            price.close,
            position_side,
            created_at=price.close_time,
        )
        self.position_manager.fill(order)
        self.process_filled_order(order)

    def get_orders_by_side(self, side: str) -> list[Order]:
        orders = filter(lambda order: order.side == side, self.orders.values())
        return sorted(orders, key=lambda x: x.created_at)

    def process_orders(self):
        for order in list(self.orders.values()):
            # handler is just a function
            handler = self.order_handlers.get(order.type, self.handle_stop_order)
            handler(order)

    def handle_market_order(self, order: Order):
        self.position_manager.fill(order)
        self.process_filled_order(order)
        del self.orders[order.id]

    def handle_stop_order(self, order):
        p = self.price_dataset.get_current_price()
        # if price is in the candle body then treats it as market order
        if p.low <= order.price <= p.high:
            self.handle_market_order(order)
