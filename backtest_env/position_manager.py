from backtest_env.constants import LONG, SHORT
from backtest_env.order import Order
from backtest_env.position import Position
from backtest_env.price import PriceData


class PositionManager:
    def __init__(self, data: PriceData, initial_balance: float):
        self.long = Position(LONG)
        self.short = Position(SHORT)
        self.balance = initial_balance
        self.margin = 0.0
        self.data = data

    def fill(self, order: Order):
        if order.positionSide == LONG:
            self.long.update(order)
            self.balance -= order.quantity * order.price
        else:
            self.short.update(order)
            self.margin += order.quantity * order.price

    def close(self):
        price = self.data.get_open_price()
        self.balance += (self.long.quantity - self.short.quantity) * price + self.margin
        self.margin = 0.0
        self.long.close()
        self.short.close()