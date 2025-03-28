from backtest_env.base.order import Order, OrderType
from backtest_env.base.side import PositionSide, OrderSide
from backtest_env.price import Price


class LimitOrder(Order):
    def __init__(
        self,
        side: OrderSide,
        quantity: float,
        symbol: str,
        price: float,
        position_side: PositionSide = None,
        created_at: int = 0,
    ):
        super().__init__(side, quantity, symbol, price, position_side, created_at)
        self.type = OrderType.Limit

    def update(self, price: Price):
        self.emit_order_filled(price.close_time) if price.low <= self.price <= price.high else None
