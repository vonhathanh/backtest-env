from backtest_env.order import Order
from backtest_env.constants import LONG, SHORT, BUY, SELL
from abc import ABC, abstractmethod


class Position(ABC):

    def __init__(self):
        self.quantity = 0.0
        self.avg_price = 0.0

    def close(self):
        self.quantity = 0.0
        self.avg_price = 0.0

    def decrease(self, delta: float):
        if self.quantity < delta:
            raise ValueError("position.quantity < delta")

        self.quantity -= delta

        if self.quantity == 0.0:
            self.avg_price = 0.0

    def increase(self, order: Order):
        if order.quantity <= 0:
            raise ValueError("order's quantity is invalid (<=0)")

        self.avg_price = ((self.quantity * self.avg_price + order.quantity * order.price) /
                          (self.quantity + order.quantity))
        self.quantity += order.quantity

    @abstractmethod
    def get_pnl(self, price: float) -> float:
        pass

    @abstractmethod
    def update(self, order: Order):
        pass


class LongPosition(Position):

    def __init__(self):
        super().__init__()
        self.side = LONG

    # TODO: test pnl()
    def get_pnl(self, price: float) -> float:
        return self.quantity * (price - self.avg_price)

    # TODO: test update()
    def update(self, order: Order):
        self.increase(order) if order.side == BUY else self.decrease(order.quantity)


class ShortPosition(Position):

    def __init__(self):
        super().__init__()
        self.side = SHORT

    def get_pnl(self, price: float) -> float:
        return self.quantity * (self.avg_price - price)

    def update(self, order: Order):
        self.increase(order) if order.side == SELL else self.decrease(order.quantity)
