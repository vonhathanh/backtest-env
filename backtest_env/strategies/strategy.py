from typing import TypeVar, Type

from backtest_env.backend import Backend
from abc import ABC, abstractmethod

from backtest_env.price import PriceData

T = TypeVar("T", bound="Strategy")


class Strategy(ABC):
    # base class for all strategies
    # contains logics to enter/exit trades, close positions
    def __init__(self, params: dict = None):
        self.params = params
        self.data = PriceData(params)
        self.backend = Backend(params["init_balance"], self.data)

    @abstractmethod
    def run(self):
        # strategy will: validate system's state: orders, positions,...
        # inspect new input data: prices, indicators,... from backend
        # create orders if necessary
        # order can be normal buy/sell order or a special action such as cancel orders, close positions
        pass

    @classmethod
    def from_cfg(cls: Type[T], params):
        return cls(params)