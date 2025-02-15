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
        self.process_previous_orders_and_current_positions()
        self.look_for_opportunities()

    def process_previous_orders_and_current_positions(self):
        self.order_manager.process_orders()

        pnl = self.position_manager.get_pnl()

        if pnl > 0.1:
            self.position_manager.close_all_positions()

    def look_for_opportunities(self):
        pending_orders = self.order_manager.get_orders()

        if len(pending_orders) >= 1 or self.position_manager.get_number_of_active_positions() >= 1:
            return

        side = BUY if random.random() <= 0.5 else SELL

        order = Order(OrderType.Market, side, 1.0, self.symbol, self.data.get_open_price(), to_position(side))

        self.order_manager.add_order(order)