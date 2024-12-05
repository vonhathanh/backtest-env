from dataclasses import dataclass
from typing import Optional

import numpy as np

from backtest_env.constants import BUY


@dataclass
class Position:
    long: float = 0.0
    short: float = 0.0

    def __len__(self):
        return 1 - (self.long == 0) + 1 - (self.short == 0)


@dataclass
class Order:
    price: Optional[float]
    symbol: str
    side: str
    type: str
    positionSide: Optional[str]
    quantity: float
    id: str


class Backend:
    # dictionary where key is order id and value is the order parameter
    pending_orders: dict[str, Order] = {}
    position: Position = Position(0, 0)
    # available cash (in $)
    balance: float = 0.0
    # index of current data point, data usually be time-series type
    cur_idx = -1
    # data will be initialized by env
    # each item is a list of: (Open time,Open,High,Low,Close,Close time)
    data = None

    def add_single_order(self, order: Order):
        self.pending_orders[order.id] = order

    def add_orders(self, orders: list[Order]):
        [self.add_single_order(order) for order in orders]

    def cancel_all_pending_orders(self):
        for order_id in self.pending_orders.keys():
            self.cancel_order(order_id)

    def cancel_order(self, order_id):
        # in reality, call OrderDispatcher.cancel()
        del self.pending_orders[order_id]

    def close_all_positions(self):
        price = self.get_last_close_price()
        # check long & short position !=0
        # if yes, set them to 0 and update balance
        if self.position.long != 0:
            self.balance += self.position.long * price
            self.position.long = 0.0

        if self.position.short != 0:
            self.balance -= self.position.short * price
            self.position.short = 0.0

    def fill_order(self, order: Order):
        # use open price because order was submitted with close price of the previous candle
        price = self.get_prices()[1] if not order.price else order.price
        # determine the amount cash needed for the order
        required_cash = order.quantity * price
        # if not enough cash -> raise an error
        if required_cash > self.get_balance():
            print(f"{order=} can't be filled, reason, insufficient fund")
        else:
            print(f"order {order.id} filled")
            self.update_position(order, required_cash)

        del self.pending_orders[order.id]

    def update_position(self, order: Order, required_cash: float):
        # open/update position based on order symbol and side
        if order.side == BUY:
            self.position.long += order.quantity
            # subtract the amount of cash required for order
            self.balance -= required_cash
        else:
            # short means we're borrowing tokens from the exchange and sell them,
            # so we increase the current balance and position's debt too
            self.position.short += order.quantity
            self.balance += required_cash
        print(f"Open price: {self.get_last_open_price()}, "
              f"position: {self.position}, "
              f"total balance: {self.get_total_wealth()}")

    def get_pending_orders(self) -> dict:
        return self.pending_orders

    def get_positions(self) -> Position:
        return self.position

    def get_balance(self) -> float:
        """
        :return: available balance in $ (debt is also included)
        """
        return self.balance - self.position.short * self.get_last_open_price()

    def get_prices(self, size: int = 1) -> np.ndarray | float:
        size = min(self.cur_idx, size)
        return self.data[self.cur_idx - size:self.cur_idx] if size > 1 else self.data[self.cur_idx]

    def get_last_close_price(self) -> float:
        return self.data[self.cur_idx][4]

    def get_last_open_price(self) -> float:
        return self.data[self.cur_idx][1]

    def get_total_wealth(self):
        """
        :return: total balance in $ (long and short position's value are included)
        """
        price = self.get_last_open_price()
        return self.balance + self.position.long * price - self.position.short * price
