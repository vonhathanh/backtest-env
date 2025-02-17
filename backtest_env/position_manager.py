from backtest_env.constants import LONG
from backtest_env.order import Order
from backtest_env.position import LongPosition, ShortPosition, Position
from backtest_env.price import PriceData


class PositionManager:
    def __init__(self, data: PriceData, initial_balance: float):
        self.long = LongPosition()
        self.short = ShortPosition()
        self.initial_balance = initial_balance # used to check real pnl
        self.balance = initial_balance
        self.margin = 0.0
        self.data = data

    def fill(self, order: Order):
        if order.position_side == LONG:
            self.long.update(order)
            self.balance -= order.quantity * order.price
        else:
            self.short.update(order)
            self.margin += order.quantity * order.price

    def close_all_positions(self):
        price = self.data.get_open_price()
        self.balance += (self.long.quantity - self.short.quantity) * price + self.margin
        self.margin = 0.0
        self.long.close()
        self.short.close()

    def get_positions(self) -> tuple[Position, Position]:
        return self.long, self.short

    def get_number_of_active_positions(self) -> int:
        return (self.long.quantity > 0.0) + (self.short.quantity > 0.0)

    def get_pnl(self, price: float = 0.0):
        price = price if price else self.data.get_open_price()
        return self.long.value(price) - self.short.value(price) + self.balance - self.initial_balance + self.margin