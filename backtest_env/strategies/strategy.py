from typing import TypeVar, Type

from backtest_env.backend import Backend

T = TypeVar("T", bound="Strategy")

class Strategy:
    # base class for all strategies
    # contains logics to enter/exit trades, close positions
    def __init__(self, params: dict = None):
        self.params = params

    def run(self, backend: Backend):
        # agent serves as the backend for strategy to query data
        # strategy will: validate agent's state: orders, positions,...
        # inspect new input data: prices, indicators,... from agent
        # create orders if necessary
        # order can be normal buy/sell order or a special action such as cancel orders, close positions
        pass

    @classmethod
    def from_cfg(cls: Type[T], params):
        return cls(params)