from backtest_env.backend import Backend
from backtest_env.strategies import Strategy


class TrendFollower(Strategy):
    """
    1) Open both long and short at daily candle close price
    2) Place n limit long orders at the upper side of the entry price.
    3) Place n limit short orders at the lower side of the entry price.
       Each long/short order has equal price difference with its predecessor/successor
    4) Price difference is the average 1h-4h candle's length
    5) To avoid complexity, we'll place 20 orders at both sides
    6) Close all positions/orders at the end of the next daily candle (we can consider another closing strategy)
    7) Test this one with highly volatile symbols
    8) Need an indicator/measure to know which pair is volatile -> daily average change in percentage
    This strategy only work when there is little wick in the candle body: engulfing,
    How do we reduce the risk when the market is not giving us the right candle?
    - Trail stoploss
    """
    def __init__(self, params):
        super().__init__(params)
        self.interval = 0.0
        self.grid_size = params["grid_size"]
        self.trading_size = params["trading_size"]

    def run(self, backend: Backend):
        pending_orders = backend.get_pending_orders()
        positions = backend.get_positions()
        if self.is_episode_end():
            self.update_grid_interval()
            # close all orders and positions
            backend.cancel_all_pending_orders()
            backend.close_all_positions()
        else:
            # start new grid or update the current grid
            if self.is_grid_empty():
                self.start_new_grid()
            else:
                self.update_grid()

    def start_new_grid(self):
        # get latest close price
        price = backend.get_prices()
        # place grid orders
        self.place_grid_orders(price, BUY)
        self.place_sell_orders(price, SELL)