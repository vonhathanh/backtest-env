from dataclasses import dataclass

from backtest_env.constants import BUY
from backtest_env.order import Order
from backtest_env.price import PriceData


@dataclass
class Position:
    long: float = 0.0
    short: float = 0.0

    def __len__(self):
        return 1 - (self.long == 0) + 1 - (self.short == 0)

    def close(self):
        self.long = 0.0
        self.short = 0.0


class Backend:
    # dictionary where key is order id and value is the order parameter
    pending_orders: dict[str, Order] = {}
    deleted_orders: list[str] = []
    position: Position = Position(0, 0)
    # available cash (in $)
    balance: float = 0.0

    def __init__(self, balance: float, prices: PriceData):
        self.balance = balance
        self.prices = prices

    def add_order(self, order: Order):
        self.pending_orders[order.id] = order

    def add_orders(self, orders: list[Order]):
        [self.add_order(order) for order in orders]

    def cancel_all_pending_orders(self):
        self.pending_orders = {}

    def cancel_order(self, order_id):
        del self.pending_orders[order_id]

    def remove_processed_orders(self):
        # delete processed orders
        for order_id in self.deleted_orders:
            del self.pending_orders[order_id]
        self.deleted_orders.clear()

    def process_pending_orders(self):
        # process all pending orders
        for order in self.pending_orders.values():
            if order.type == "MARKET":
                self.handle_market_order(order)
            elif order.type == "LIMIT":
                self.handle_limit_order(order)
            elif order.type == "STOP":
                self.handle_stop_order(order)
            elif order.type == "TAKE_PROFIT":
                pass
            elif order.type == "STOP_MARKET":
                pass
            elif order.type == "TAKE_PROFIT_MARKET":
                pass
            elif order.type == "TRAILING_STOP_MARKET":
                pass
            else:
                raise ValueError("order type must be: "
                                 "MARKET, LIMIT, STOP, TAKE_PROFIT, STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET")
        self.remove_processed_orders()

    def handle_market_order(self, order: Order):
        # determine the amount cash needed for the order
        required_cash = order.quantity * order.price
        # if not enough cash -> raise an error
        if required_cash > self.get_balance():
            raise ValueError(f"{order=} can't be filled, reason, insufficient fund")
        else:
            print(f"order {order.id} filled")
            self.update_position(order, required_cash)

        self.deleted_orders.append(order.id)


    def handle_limit_order(self, order):
        pass

    def handle_stop_order(self, order):
        p = self.prices.get_current_price()
        # move from high to low to check if the order price is in this range
        # high > order price which means order can be filled
        if order.price <= p.high and order.side == "BUY":
            self.handle_market_order(order)
        # low < order price which means order can be filled
        if order.price >= p.low and order.side == "SELL":
            self.handle_market_order(order)

    def close_all_positions(self):
        price = self.prices.get_current_price().close
        # check long & short position !=0
        # if yes, set them to 0 and update balance
        self.balance += (self.position.long - self.position.short) * price
        self.position.close()

        print(f"balance after close all position: {self.balance}")

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

        print(f"Open price: {self.prices.get_current_price().open}, "
              f"position: {self.position}, "
              f"total balance: {self.get_total_wealth()}")

    def get_pending_orders(self):
        return self.pending_orders

    def get_pending_orders_with_side(self):
        longs, shorts = [], []
        for order in self.pending_orders.values():
            if order.side == "BUY":
                longs.append(order)
            else:
                shorts.append(order)
        return longs, shorts


    def get_positions(self) -> Position:
        return self.position

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
