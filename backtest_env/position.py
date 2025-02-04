from dataclasses import dataclass

from backtest_env.order import Order


@dataclass
class Position:
    long: float = 0.0
    short: float = 0.0
    balance: float = 0.0

    def __len__(self):
        return 1 - (self.long == 0) + 1 - (self.short == 0)

    def close(self):
        self.long = 0.0
        self.short = 0.0

    def fill(self, order: Order):
        # determine the amount cash needed for the order
        required_cash = order.quantity * order.price
        # if not enough cash -> raise an error
        if required_cash > self.get_balance():
            raise ValueError(f"{order=} can't be filled, reason, insufficient fund")
        else:
            print(f"order {order.id} filled")
            self.update_position(order, required_cash)