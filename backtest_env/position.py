from backtest_env.order import Order
from backtest_env.constants import LONG, SHORT, BUY, SELL
from abc import ABC, abstractmethod


class Position(ABC):

    def __init__(self):
        self.side = ''
        self.quantity = 0.0
        self.avg_price = 0.0

    def close(self):
        self.quantity = 0.0
        self.avg_price = 0.0

    def cost(self) -> float:
        return self.quantity * self.avg_price

    def value(self, price: float):
        return self.quantity * price

    def decrease(self, delta: float):
        self.quantity -= delta

        if self.quantity == 0.0:
            self.avg_price = 0.0

    def increase(self, order: Order):
        self.avg_price = round(((self.quantity * self.avg_price + order.quantity * order.price) /
                                (self.quantity + order.quantity)), 4)
        self.quantity += order.quantity

    def json(self):
        return {
            "side": self.side,
            "quantity": self.quantity,
            "averagePrice": self.avg_price
        }

    @abstractmethod
    def get_pnl(self, price: float) -> float:
        pass

    @abstractmethod
    def update(self, order: Order):
        pass

    @abstractmethod
    def validate(self, order: Order):
        pass


class LongPosition(Position):

    def __init__(self):
        super().__init__()
        self.side = LONG

    def get_pnl(self, price: float) -> float:
        return round(self.quantity * (price - self.avg_price), 4)

    def validate(self, order: Order):
        assert order.quantity > 0
        if order.side == SELL:
            assert order.quantity <= self.quantity

    def update(self, order: Order):
        self.validate(order)
        self.increase(order) if order.side == BUY else self.decrease(order.quantity)


class ShortPosition(Position):

    def __init__(self):
        super().__init__()
        self.side = SHORT

    def get_pnl(self, price: float) -> float:
        return round(self.quantity * (self.avg_price - price), 4)

    def validate(self, order: Order):
        assert order.quantity > 0
        if order.side == BUY:
            assert order.quantity <= self.quantity

    def update(self, order: Order):
        self.validate(order)
        self.increase(order) if order.side == SELL else self.decrease(order.quantity)
