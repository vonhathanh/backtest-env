import random

from backtest_env.dto import BacktestParam
from backtest_env.order import OrderType
from backtest_env.strategies.strategy import Strategy
from backtest_env.utils import create_order
from backtest_env.constants import *


class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, params: BacktestParam):
        super().__init__(params)
        self.symbol = params.symbol

    def run(self):
        while self.data.step():
            self.order_manager.process_orders()
            self.update()
        print("Backtest finished")

    def update(self):
        pending_orders = self.order_manager.get_orders()
        positions = self.position_manager.get_positions()

        if len(pending_orders) >= 2 or len(positions) >= 2:
            return

        side = BUY if random.random() <= 0.5 else SELL

        order = create_order(OrderType.Market, self.symbol, side, self.data.get_close_price(), 1.0)

        self.order_manager.add_order(order)
