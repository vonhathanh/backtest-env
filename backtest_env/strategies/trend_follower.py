import numpy as np

import backtest_env.utils as utils
from backtest_env.dto import TrendFollowerArgs
from backtest_env.order import OrderType, Order
from backtest_env.strategies import Strategy
from backtest_env.constants import BUY, SELL

class TrendFollower(Strategy):
    """
    1) Open both long and short at daily candle close price
    2) Place n limit long orders at the upper side of the entry price.
    3) Place n limit short orders at the lower side of the entry price.
       Each long/short order has equal step size with its predecessor/successor
    4) Price difference is the average 1h-4h candle's length
    5) To avoid complexity, we'll place 20 orders at both sides
    6) Close all positions/orders at the end of the next daily candle (we can consider another closing strategy)
    7) Test this one with highly volatile symbols
    8) Need an indicator/measure to know which pair is volatile -> daily average change in percentage
    This strategy only work when there is little wick in the candle body: engulfing,
    How do we reduce the risk when the market is not giving us the right candle?
    - Trail stoploss
    """
    def __init__(self, args: TrendFollowerArgs):
        super().__init__(args)
        self.symbol = args.symbol
        # how many grid orders will be placed
        self.grid_size = args.gridSize

        self.order_size = args.orderSize

        # the difference in percentage of the next grid order compared to current order
        # example, current grid order: buy btc at 1000$, step_size = 0.01, so the next order will be placed at
        # 1000*(1+0.01) = 1010$
        self.step_size = 0.01
        # interval is used to calculate step_size dynamically, step_size = daily average change / interval.
        # interval usually will be around [4, 8] depends on symbol and user's preference
        self.interval = args.interval

        # number of 1d candles being stored to calculate daily average change
        self.candle_cache_size = args.candleCacheSize
        self.candles = []
        # these values will be used to form daily candle based on smaller candles data
        self.open, self.high, self.low, self.close = 0.0, 0.0, np.inf, 0.0

    @classmethod
    def from_cfg(cls, kwargs):
        args = TrendFollowerArgs(**kwargs)
        return cls(args)

    @classmethod
    def get_required_params(cls):
        return {"Grid Size": {"type": "int", "defaultValue": 5},
                "Order Size": {"type": "int", "defaultValue": 100},
                "Interval": {"type": "int", "defaultValue": 4},
                "Candle Cache Size": {"type": "int", "defaultValue": 10}}

    def update(self):
        self.update_statistic()
        self.order_manager.process_orders()

        if self.is_episode_end():
            self.order_manager.cancel_all_orders()
            self.position_manager.close_all_positions()

        # only start the strategy when we've collected enough daily candles
        if len(self.candles) >= self.candle_cache_size:
            self.update_grid()

    def is_episode_end(self) -> bool:
        # check if current candle is the first candle in the day (open time = 00:00:00 AM GMT)
        # time is in millisecond, so we use 86_400_000
        # TODO: check if all daily candles start at 00:00::00 UTC
        price = self.data.get_current_price()
        return price.open_time % 86_400_000 == 0 or self.data.idx == 0

    def update_statistic(self):
        self.update_candle_cache()
        # calculate step_size if we've gathered enough candles
        if len(self.candles) >= self.candle_cache_size:
            self.update_step_size()

    def update_candle_cache(self):
        price = self.data.get_current_price()
        # maintain a running high and low to store the highest, lowest price in a day
        self.high = max(self.high, price.high)
        self.low = min(self.low, price.low)

        # to check for open time in candle, just mod it with 86_400_000
        if price.open_time % 86_400_000 == 0:
            self.open = price.open
        # close time is smaller than next open time by 1 millisecond
        if (int(price.close_time) + 1) % 86_400_000 == 0:
            self.close = price.close
            self.store_new_candle()

    def store_new_candle(self):
        # edge case, no open candle
        if self.open == 0:
            self.open = self.close

        self.candles.append((self.open, self.high, self.low, self.close))
        # reset variables, open & close aren't resetted because their value are determined by time
        self.high, self.low = 0.0, np.inf

    def update_step_size(self):
        prices = np.array(self.candles[-self.candle_cache_size:])
        # our formula for determine change per day is: (high - low) / open / step
        changes = np.abs(prices[:, 1] - prices[:, 2]) / prices[:, 0]
        # step_size can't be too small, so we set 0.005 as minimum
        self.step_size = round(max(np.mean(changes) / self.interval, 0.005), 3)

    def update_grid(self):
        self.place_grid_orders(BUY)
        self.place_grid_orders(SELL)

    def place_grid_orders(self, side: str):
        orders = self.order_manager.get_open_orders(side=side)
        num_unfill_orders = self.grid_size - len(orders)
        assert num_unfill_orders >= 0
        # determine entry price for new order, use current price if grid is empty
        # else use the latest order's price as starting point
        price = self.data.get_close_price() if not orders else orders[-1].price

        for i in range(0, num_unfill_orders):
            price = utils.get_tp(price, self.step_size, side)
            order = Order(OrderType.Limit, side, self.order_size, self.symbol, price, utils.to_position(side))
            self.order_manager.add_order(order)
