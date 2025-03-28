import time

from backtest_env.base.order import Order, OrderType
from backtest_env.orders.limit import LimitOrder
from backtest_env.price import Price


class OneCancelOtherOrder(Order):
    def __init__(
        self,
        sl: float,
        tp: float,
        sl_quantity: float,
        tp_quantity: float,
        side: str,
        symbol: str,
        price: float,
        position_side: str,
        created_at: int = 0,
    ):
        super().__init__(side, 0.0, symbol, price, created_at)
        self.type = OrderType.OCO
        self.sl = sl
        self.tp = tp
        self.sl_quantity = sl_quantity
        self.tp_quantity = tp_quantity
        assert self.sl_quantity > 0
        assert self.tp_quantity > 0

    def update(self, price: Price):
        if price.low <= self.price <= price.high:
            self.fill(price)
            self.emit("order.filled", self.json())

    def fill(self):
        sub_orders = []
        if self.sl:
            stoploss = LimitOrder(
                self.side.reverse(),
                self.sl_quantity,
                self.symbol,
                self.sl,
                self.position_side,
                int(time.time()),
            )
            sub_orders.append(stoploss)
        if self.tp:
            take_profit = LimitOrder(
                self.side.reverse(),
                self.tp_quantity,
                self.symbol,
                self.sl,
                self.position_side,
                int(time.time()),
            )
            sub_orders.append(take_profit)
        return sub_orders
