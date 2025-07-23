from backtest_env.base.order import Order, OrderType
from backtest_env.base.side import PositionSide, OrderSide
from backtest_env.price import Price


class LimitOrder(Order):
    """
    A limit order is designed to execute a trade at a specific price or better,
    ensuring that a buyer does not pay more than a desired price or a seller receives at least a specified price.
    This type of order is useful when targeting a specific price point,
    although it does not guarantee execution if the market does not reach the set price
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
        self.type = OrderType.Limit

    def update(self, price: Price):
        self.emit_order_filled(price.close_time) if price.low <= self.price <= price.high else None
