from eventure import Event
from socketio import Client

from backtest_env.base.event_hub import EventHub
from backtest_env.base.order import Order
from backtest_env.base.side import PositionSide, OrderSide
from backtest_env.orders.close_position import ClosePositionOrder
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet, Price


class OrderManager(EventHub):
    def __init__(
        self,
        position_manager: PositionManager,
        price_dataset: PriceDataSet,
        sio: Client = None,
        symbol: str = "",
    ):
        super().__init__(sio)
        self.orders: dict[str, Order] = {}
        self.filled_orders: list[Order] = []
        self.position_manager = position_manager
        self.price_dataset = price_dataset
        self.symbol = symbol
        self.setup_event_handlers()

    def setup_event_handlers(self):
        self.event_bus.subscribe("order.filled", self.on_order_filled)
        self.event_bus.subscribe("oco_order.filled", self.on_oco_order_filled)

    def get_all_orders(self) -> list[Order]:
        return list(self.orders.values())

    def get_order_history(self) -> list[Order]:
        return self.filled_orders

    def add_order(self, order: Order):
        self.orders[order.id] = order
        self.emit_to_frontend("new_orders", [order.json()])

    def add_orders(self, orders: list[Order]):
        for order in orders:
            # we don't call self.add_order() because want to trigger the new_orders event in bulk
            self.orders[order.id] = order
        self.emit_to_frontend("new_orders", [order.json() for order in orders])

    def cancel_all_orders(self):
        self.orders = {}
        self.emit_to_frontend("current_orders", [])

    def close_all_positions(self, price: Price):
        [long, short] = self.position_manager.get_positions()
        if long.is_active():
            self.close_position(PositionSide.LONG, long.quantity, price)
        if short.is_active():
            self.close_position(PositionSide.SHORT, short.quantity, price)

    def close_position(self, position_side: str, quantity: float, price: Price):
        side = OrderSide.SELL if position_side == PositionSide.LONG else OrderSide.BUY
        order = ClosePositionOrder(
            side,
            quantity * price.close,
            self.symbol,
            price.close,
            position_side,
            price.close_time,
        )
        self.add_order(order)
        order.update(price)

    def get_orders_by_side(self, side: str) -> list[Order]:
        orders = filter(lambda order: order.side == side, self.orders.values())
        return sorted(orders, key=lambda x: x.created_at)

    def process_orders(self):
        for order in list(self.orders.values()):
            order.update(self.price_dataset.get_current_price())

    def on_order_filled(self, event: Event):
        order: Order = event.data
        self.position_manager.fill(order)
        self.filled_orders.append(order)
        self.emit_to_frontend("order_filled", order.json())
        del self.orders[order.id]

    def on_oco_order_filled(self, order: Order):
        pass
