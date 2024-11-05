from backtest_env.backend import Backend
from backtest_env.strategies import Strategy


class TrendFollower(Strategy):
    """
    1) Open both long and short at daily candle close price
    2) Place limit long orders at the upper side of the entry price.
    3) Place limit short orders at the lower side of the entry price.
       Each long/short order has equal price difference with its predecessor/successor
    4) Price difference is the average 1h-4h candle's length
    5) To avoid complexity, we'll place 20 orders at both sides
    6) Close all positions/orders at the end of the next candle
    7) Test this one with highly volatile symbols
    8) Need an indicator/measure to know which pair is volatile
    This strategy only work when there is little wick in the candle body: engulfing,
    How do we reduce the risk when the market is not giving us the right candle?
    - Trail stoploss
    - 
    """
    def __init__(self, params):
        super().__init__(params)

    def run(self, backend: Backend):
        # get pending orders and positions
        pending_orders = backend.get_pending_orders()
        positions = backend.get_positions()
        # close all orders and positions
        backend.cancel_all_pending_orders()
        backend.close_all_positions()
        # start new grid
        # get latest close price
        price = backend.get_prices()
        # get statistics like grid interval, size from price history
        interval = calculate_grid_interval()
        grid_size = calculate_grid_size()
        # place grid orders
        place_grid_orders(price, BUY, grid_size, interval, self.params["quantity"])
        place_sell_orders(price, BUY, grid_size, interval, self.params["quantity"])