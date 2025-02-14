from typing import TypeVar, Type
from abc import ABC, abstractmethod

from backtest_env.dto import Args
from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceData

T = TypeVar("T", bound="Strategy")


class Strategy(ABC):
    # base class for all strategies
    def __init__(self, args: Args):
        self.data = PriceData(args.symbol, args.timeframe, args.start_time, args.end_time)
        self.position_manager = PositionManager(self.data, args.initial_balance)
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
    def from_cfg(cls: Type[T], args: Args):
        return cls(args)

    @classmethod
    def get_required_params(cls: Type[T]):
        return {}