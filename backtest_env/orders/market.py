from backtest_env.base.order import Order, OrderType
from backtest_env.base.side import OrderSide, PositionSide
from backtest_env.price import Price


class MarketOrder(Order):
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
        self.type = OrderType.Market

    def update(self, price: Price):
        self.emit_order_filled(price.close_time)
