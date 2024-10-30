from backtest_env.strategies.strategy import Strategy
from backtest_env.utils import market_order
from backtest_env.constants import *

class Baseline(Strategy):
    # base class for strategy
    # contains logics to enter/exit trades, close positions
    def __init__(self, params):
        super().__init__()
        self.params = params


    def run(self, data: dict) -> list:
        # order can be normal buy/sell order or a special action such as cancel orders, close positions
        order = market_order(self.params["symbol"], BUY, 0.0, 1.0)
        return [order]