import random

from backtest_env.backend import Backend
from backtest_env.strategies.strategy import Strategy
from backtest_env.utils import market_order
from backtest_env.constants import *

class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, params):
        super().__init__(params)


    def run(self, backend: Backend) -> list:
        pending_orders = backend.get_pending_orders()
        positions = backend.get_positions()

        if len(pending_orders) >= 2 or len(positions) >= 2:
            return []

        side = BUY if random.random() <= 0.5 else SELL

        order = market_order(self.params["symbol"], side, 0.0, 1.0)

        return [order]