import random

from backtest_env.base.side import OrderSide
from backtest_env.dto import Args
from backtest_env.base.strategy import Strategy
from backtest_env.orders.market import MarketOrder


class Baseline(Strategy):
    # this strategy represents as an example of real trading strategy
    def __init__(self, args: Args):
        super().__init__(args)
        random.seed(1993)

    def update(self):
        self.update_orders_and_positions()
        self.look_for_opportunities()

    def update_orders_and_positions(self):
        self.order_manager.process_orders()

        pnl = self.position_manager.get_unrealized_pnl(self.data.get_close_price())

        if pnl > 1 or pnl < -1:
            self.order_manager.close_all_positions(self.data.get_current_price())

    def look_for_opportunities(self):
        pending_orders = self.order_manager.get_all_orders()

        if len(pending_orders) >= 1 or self.position_manager.get_total_active_positions() >= 1:
            return

        side = OrderSide.BUY if random.random() <= 0.5 else OrderSide.SELL

        order = MarketOrder(
            side,
            1.0,
            self.symbol,
            self.data.get_close_price(),
            created_at=self.data.get_close_time(),
        )

        self.order_manager.add_order(order)
