from backtest_env.base.side import OrderSide
from backtest_env.orders.market import MarketOrder


def create_long_order(
    side: str = OrderSide.BUY,
    quantity=1.0,
    symbol: str = "X",
    price: float = 100.0,
):
    return MarketOrder(side, quantity * price, symbol, price)


def create_short_order(
    side: str = OrderSide.SELL,
    quantity=1.0,
    symbol: str = "X",
    price: float = 100.0,
):
    return MarketOrder(side, quantity * price, symbol, price)
