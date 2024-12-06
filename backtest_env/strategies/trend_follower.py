import numpy as np
from datetime import datetime

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
        self.interval = 0.005
        self.grid_size = params["grid_size"]
        self.trading_size = params["trading_size"]
        self.symbol = params["symbol"]
        self.min_num_daily_candles = params["min_num_daily_candles"]
        # interval = daily_change/step
        self.step = params["step"]
        # three ways to calculate self.interval
        # 1. Hard coded
        # 2. Add daily candle data and inference the interval from that
        # 3. Store daily candles in self and derive the interval
        # we'll go with 3rd method, is complicated, but works in both real and simulated env
        self.daily_candles = []
        # parameters of daily candle
        self.high = 0.0
        self.low = 2 << 64 # init low to maximum value of int64
        self.open = 0.0
        self.close = 0.0

    def run(self):
        self.update_grid_interval()

        if self.is_episode_end():
            price = self.backend.get_prices()
            print(f"start new daily candle at: {datetime.fromtimestamp(int(price[0])//1000)}")
            print(f"previous candle is: {self.daily_candles[-1] if len(self.daily_candles) > 0 else None}")
            # close all orders and positions
            self.backend.cancel_all_pending_orders()
            self.backend.close_all_positions()

        # only start the strategy when we've collected enough daily candles
        if len(self.daily_candles) >= self.min_num_daily_candles:
            # start new grid or update the current grid
            self.update_grid()

    def is_episode_end(self) -> bool:
        # check if current candle is the first candle in the day (open time = 00:00:00 AM GMT)
        price = self.backend.get_prices()
        # TODO: check if all daily candles start at 00:00::00 UTC
        # price[0] = open time, time is in millisecond so we mod 86400*1000
        return price[0] % 86_400_000 == 0 or self.backend.cur_idx == 0

    def update_grid_interval(self):
        """
        incharge of add new daily candle and calculate average price change based on those candles
        """
        candle = self.backend.get_prices()
        # maintain a running high and low to store the highest, lowest price in a day
        self.high = max(self.high, candle[2])
        self.low = min(self.low, candle[3])

        # to check for open and close time in a daily candle, just mod them with 86_400_000
        if candle[0] % 86_400_000 == 0:
            self.open = candle[1]
        # close time is minus by 1 millisecond, so we add 1 for it
        if (int(candle[5]) + 1) % 86_400_000 == 0:
            self.close = candle[4]
            # edge case, no open candle
            if self.open == 0:
                self.open = self.close
            # store what we have so far
            self.daily_candles.append((self.open, self.high, self.low, self.close))
            # reset variables
            self.high, self.low = 0.0, 2 << 64

        # calculate grid interval if we've gathered enough candles
        if len(self.daily_candles) >= self.min_num_daily_candles:
            prices = np.array(self.daily_candles[-self.min_num_daily_candles:])
            # our formula for determine change per day is: (high - low) / open / step
            changes = np.abs(prices[:, 1] - prices[:, 2]) / prices[:, 0]
            # interval can't be too small, so we set 0.005 as minimum
            self.interval = round(max(np.mean(changes) / self.step, 0.005), 3)

    def place_grid_orders(self, orders: list[Order], side: str):
        # check if any order is filled, if yes, refill orders depend on order type
        num_unfill_orders = self.grid_size - len(orders)
        assert num_unfill_orders >= 0
        # determine entry price for new order, use current price if grid is empty
        # else use the latest order's price as starting point
        price = self.backend.get_last_close_price() if len(orders) == 0 else orders[-1].price
        if num_unfill_orders > 0:
            print(f"add new {num_unfill_orders} {side} orders to the backend")
        for i in range(0, num_unfill_orders):
            price = utils.get_tp(price, self.interval, side)
            self.backend.add_single_order(utils.create_order("STOP", self.symbol, side, price, self.trading_size))


    def update_grid(self):
        # split orders into two types
        long_orders, short_orders = self.backend.get_pending_orders(is_split=True)
        # place grid orders
        self.place_grid_orders(long_orders, BUY)
        self.place_grid_orders(short_orders, SELL)
