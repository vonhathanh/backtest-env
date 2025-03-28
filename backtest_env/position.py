from backtest_env.balance import Balance
from backtest_env.base.order import Order
from abc import ABC, abstractmethod

from backtest_env.base.side import PositionSide, OrderSide


class Position(ABC):
    def __init__(self, balance: Balance):
        self.side = ""
        self.quantity = 0.0
        self.average_price = 0.0
        self.balance = balance

    def decrease(self, order: Order):
        self.quantity -= order.quantity

        if self.quantity == 0.0:
            self.average_price = 0.0

    def increase(self, order: Order):
        total_value_in_usd = self.quantity * self.average_price + order.quantity * order.price
        total_quantity = self.quantity + order.quantity
        self.average_price = round(total_value_in_usd / total_quantity, 4)
        self.quantity += order.quantity

    def json(self):
        return {
            "side": self.side,
            "quantity": self.quantity,
            "averagePrice": self.average_price,
        }

    def is_active(self) -> bool:
        return self.quantity > 0

    def value(self, price: float) -> float:
        return round(self.quantity * price, 4)

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
    def __init__(self, balance: Balance):
        super().__init__(balance)
        self.side = PositionSide.LONG

    def get_pnl(self, price: float) -> float:
        return round(self.quantity * (price - self.average_price), 4)

    def validate(self, order: Order):
        if order.side == OrderSide.SELL:
            assert order.quantity <= self.quantity
        assert order.quantity > 0

    def update(self, order: Order):
        self.validate(order)
        self.increase(order) if order.side == OrderSide.BUY else self.decrease(order)

    def increase(self, order: Order):
        super().increase(order)
        self.balance.current -= order.quantity * order.price
        assert self.balance.current >= 0

    def decrease(self, order: Order):
        super().decrease(order)
        self.balance.current += order.quantity * order.price


class ShortPosition(Position):
    def __init__(self, balance: Balance):
        super().__init__(balance)
        self.side = PositionSide.SHORT

    def get_pnl(self, price: float) -> float:
        return round(self.quantity * (self.average_price - price), 4)

    def validate(self, order: Order):
        if order.side == OrderSide.BUY:
            assert order.quantity <= self.quantity
        assert order.quantity > 0

    def update(self, order: Order):
        self.validate(order)
        self.increase(order) if order.side == OrderSide.SELL else self.decrease(order)

    def increase(self, order: Order):
        super().increase(order)
        self.balance.margin += order.quantity * order.price

    def decrease(self, order: Order):
        super().decrease(order)
        self.balance.margin -= order.quantity * order.price
        if self.quantity == 0:
            self.balance.current += self.balance.margin
            self.balance.margin = 0
