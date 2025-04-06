from backtest_env.base.order import Order, OrderType
from backtest_env.orders.limit import LimitOrder
from backtest_env.price import Price


class OneCancelOtherOrder(Order):
    def __init__(
        self,
        sl: float,
        tp: float,
        side: str,
        amount_in_usd: float,
        symbol: str,
        price: float,
        position_side: str,
        created_at: int = 0,
    ):
        super().__init__(side, amount_in_usd, symbol, price, position_side, created_at)
        self.type = OrderType.OCO
        self.sl = sl
        self.tp = tp

    def update(self, price: Price):
        if price.low <= self.price <= price.high:
            self.fill(price)
            self.emit("order.filled", self)

    def fill(self, price: Price):
        if self.sl:
            stoploss = LimitOrder(
                self.side.reverse(),
                self.quantity * self.sl,
                self.symbol,
                self.sl,
                self.position_side,
                price.close_time,
            )
            self.emit("order.new", stoploss)
        if self.tp:
            take_profit = LimitOrder(
                self.side.reverse(),
                self.quantity * self.tp,
                self.symbol,
                self.tp,
                self.position_side,
                price.close_time,
            )
            self.emit("order.new", take_profit)
