from backtest_env.order import Order
from backtest_env.price import PriceData


class Position:
    """
    Short position/order is handle different from long position
    1) Fill short order: balance += order.quantity * price, self.short += order.quantity
    2) Close short position:
    - we pay the debt by: balance -= self.short * price
    - reset debt: self.short = 0.0
    this approach makes our balance higher than what it's actually is,
    so we need a function to calculate the real balance
    """
    def __init__(self, initial_balance, data: PriceData):
        self.long: float = 0.0
        self.short: float = 0.0
        self._balance: float = initial_balance
        self.data = data

    def __len__(self):
        return self.long != 0.0 + self.short != 0.0

    def close(self):
        profit = self.data.get_open_price() * (self.long - self.short)
        self._balance += profit

        self.long = 0.0
        self.short = 0.0

    # TODO: test get_balance()
    def get_balance(self):
        return self._balance + self.data.get_open_price() * (self.long - self.short)

    def update_position_based_on(self, order: Order, cost: float):
        if order.side == "BUY":
            self.long += order.quantity
            self._balance -= cost
        else:
            self.short += order.quantity
            self._balance += cost

    # TODO: test fill order
    def fill(self, order: Order):
        cost = order.price * order.quantity
        if cost > self.get_balance():
            raise ValueError(f"{order=} can't be filled, reason: insufficient fund")
        self.update_position_based_on(order, cost)