from backtest_env.base.order import OrderType
from backtest_env.base.side import OrderSide, PositionSide
from backtest_env.orders.market import MarketOrder


class ClosePositionOrder(MarketOrder):
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
        self.type = OrderType.ClosePosition
