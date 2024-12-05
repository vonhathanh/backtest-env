import backtest_env.utils as utils
from backtest_env.backend import Order
from backtest_env.strategies import Strategy
from backtest_env.constants import BUY, SELL


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
        self.symbol = params["symbol"]

    def run(self):
        if self.is_episode_end():
            self.update_grid_interval()
            # close all orders and positions
            self.backend.cancel_all_pending_orders()
            self.backend.close_all_positions()

        # start new grid or update the current grid
        self.update_grid()

    def is_episode_end(self) -> bool:
        # check if current candle is the first candle in daily candle (00:00:00 AM GMT)
        price = self.backend.get_prices()
        # TODO: check if all daily candles start at 00:00::00 UTC
        # price[0] = open time, time is in millisecond so we mod 86400*1000
        return price[0] % 86_400_000 == 0 or self.backend.cur_idx == 0

    def update_grid_interval(self):
        # calculate average price change in hours, minutes and update the interval attribute
        pass

    def place_grid_orders(self, orders: list[Order], side: str):
        # check if any order is filled, if yes, refill orders depend on order type
        num_unfill_orders = self.grid_size - len(orders)
        assert num_unfill_orders >= 0
        # determine entry price for new order, use current price if grid is empty
        # else use the latest order's price as starting point
        price = self.backend.get_prices() if len(orders) == 0 else orders[-1].id
        for i in range(0, num_unfill_orders):
            price = utils.get_tp(price, self.interval, side)
            self.backend.add_single_order(utils.market_order(self.symbol, side, price, self.trading_size))


    def update_grid(self):
        # split orders into two types
        long_orders, short_orders = self.backend.get_pending_orders(is_split=True)
        # place grid orders
        self.place_grid_orders(long_orders, BUY)
        self.place_grid_orders(short_orders, SELL)
