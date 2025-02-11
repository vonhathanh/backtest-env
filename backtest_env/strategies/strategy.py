from typing import TypeVar, Type
from abc import ABC, abstractmethod

from backtest_env.dto import BacktestParam
from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceData

T = TypeVar("T", bound="Strategy")


class Strategy(ABC):
    # base class for all strategies
    def __init__(self, params: BacktestParam):
        self.data = PriceData(params.symbol, params.timeframe, params.start_time, params.end_time)
        self.position_manager = PositionManager(self.data, params.initial_balance)
        self.order_manager = OrderManager(self.position_manager, self.data)

    def run(self):
        # strategy will: call self.data.step() to move forward to the next price
        # validate account's state: orders, positions,...
        # inspect new input data: prices, indicators,... from backend
        # determine the next action: submit buy/sell order, cancel orders, close positions, ...
        while self.data.step():
            self.update()
        print("Backtest finished")

    @abstractmethod
    def update(self):
        pass

    @classmethod
    def from_cfg(cls: Type[T], params: BacktestParam):
        return cls(params)

    @classmethod
    def get_required_params(cls: Type[T]):
        return {}