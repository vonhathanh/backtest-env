from backtest_env.constants import BUY
from backtest_env.order import Order
from backtest_env.price import PriceData


class Backend:
    # available cash (in $)
    balance: float = 0.0

    def __init__(self, balance: float, prices: PriceData):
        self.balance = balance
        self.prices = prices

    def close_all_positions(self):
        price = self.prices.get_close_price()
        self.balance += (self.position.long - self.position.short) * price
        self.position.close()

    def update_position(self, order: Order, required_cash: float):
        self.position.update(order)
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

        print(f"Open price: {self.prices.get_current_price().open}, "
              f"position: {self.position}, "
              f"total balance: {self.get_total_wealth()}")

    def get_pending_orders_with_side(self):
        longs, shorts = [], []
        for order in self.pending_orders.values():
            if order.side == "BUY":
                longs.append(order)
            else:
                shorts.append(order)
        return longs, shorts


    def get_balance(self) -> float:
        """
        :return: available balance in $ (debt is also included)
        """
        return self.balance - self.position.short * self.prices.get_open_price()

    def get_total_wealth(self):
        """
        :return: total balance in $ (long and short position's value are included)
        """
        price = self.prices.get_open_price()
        return round(self.balance + (self.position.long - self.position.short) * price, 4)
