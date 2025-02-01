from abc import ABC

from backtest_env.strategies import Strategy


class PausableStrategy(Strategy, ABC):
    def __init__(self, params: dict):
        super().__init__(params)
        # determine whether the strategy is being paused or not
        self.is_paused = False
