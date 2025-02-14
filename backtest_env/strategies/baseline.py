import random

from backtest_env.dto import Args
from backtest_env.order import OrderType, Order
from backtest_env.strategies.strategy import Strategy
from backtest_env.constants import *
from backtest_env.utils import to_position


class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, args: Args):
        super().__init__(args)
        self.symbol = args.symbol

    def update(self):
        self.order_manager.process_orders()

        pending_orders = self.order_manager.get_orders()

        if len(pending_orders) >= 2 or len(self.position_manager.get_number_of_active_positions()) >= 2:
            return

        side = BUY if random.random() <= 0.5 else SELL

        order = Order(self.data.get_open_price(), self.symbol, side, OrderType.Market, to_position(side), 1.0)

        self.order_manager.add_order(order)
