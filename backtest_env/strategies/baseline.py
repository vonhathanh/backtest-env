import random

from backtest_env.strategies.strategy import Strategy
from backtest_env.utils import create_order
from backtest_env.constants import *

class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, params):
        super().__init__(params)

    def run(self) -> list:
        pending_orders = self.backend.get_pending_orders()
        positions = self.backend.get_positions()

        if len(pending_orders) >= 2 or len(positions) >= 2:
            return []

        side = BUY if random.random() <= 0.5 else SELL

        order = create_order("MARKET", self.params["symbol"], side, self.backend.get_prices()[4], 1.0)

        return [order]