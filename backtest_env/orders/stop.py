from backtest_env.base.order import Order, OrderType
from backtest_env.base.side import PositionSide, OrderSide
from backtest_env.price import Price


class StopOrder(Order):
    """
    stop order triggers a market order once a specified price, known as the stop price, is reached.
    This means that once the stop price is met, the order will be filled at the best available market price,
    which may be different from the stop price.
    Stop orders are often used to limit losses or to capture gains by exiting a position
    once a certain price level is breached, but they do not guarantee the final execution price
    """

    def __init__(
        self,
        side: OrderSide,
        amount_in_usd: float,
        symbol: str,
        price: float,
        position_side: PositionSide = None,
        created_at: int = 0,
    ):
        super().__init__(side, amount_in_usd, symbol, price, position_side, created_at)
        self.type = OrderType.Stop

    def update(self, price: Price):
        self.emit_order_filled(price.close_time) if price.low <= self.price <= price.high else None
