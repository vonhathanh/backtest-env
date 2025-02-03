import random

from backtest_env.strategies.strategy import Strategy
from backtest_env.utils import create_order
from backtest_env.constants import *


class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, params):
        super().__init__(params)

    def run(self):
        while self.data.step():
            self.backend.process_pending_orders()
            self.update()

    def update(self):
        pending_orders = self.backend.get_pending_orders()
        positions = self.backend.get_positions()

        if len(pending_orders) >= 2 or len(positions) >= 2:
            return

        side = BUY if random.random() <= 0.5 else SELL

        order = create_order("MARKET", self.params["symbol"], side, self.data.get_close_price(), 1.0)

        self.backend.add_orders([order])
