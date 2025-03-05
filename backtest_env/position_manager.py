from backtest_env.constants import LONG
from backtest_env.order import Order
from backtest_env.position import LongPosition, ShortPosition, Position


class PositionManager:
    def __init__(self, initial_balance: float):
        self.long = LongPosition()
        self.short = ShortPosition()
        self.initial_balance = initial_balance  # used to check real pnl
        self.balance = initial_balance
        self.margin = 0.0

    def fill(self, order: Order):
        if order.position_side == LONG:
            self.long.update(order)
            self.balance -= order.quantity * order.price
            assert self.balance >= 0
        else:
            self.short.update(order)
            self.margin += order.quantity * order.price
            assert self.margin <= self.balance

    def close_all_positions(self, price: float):
        self.balance += (self.long.quantity - self.short.quantity) * price + self.margin
        self.margin = 0.0
        self.long.close()
        self.short.close()

    def get_positions(self) -> tuple[Position, Position]:
        return self.long, self.short

    def get_number_of_active_positions(self) -> int:
        return (self.long.quantity > 0.0) + (self.short.quantity > 0.0)

    def get_unrealized_pnl(self, price: float) -> float:
        return (
            self.long.value(price)
            - self.short.value(price)
            + self.balance
            - self.initial_balance
            + self.margin
        )

    def get_pnl(self):
        return self.balance - self.initial_balance
