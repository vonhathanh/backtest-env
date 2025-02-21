from asyncio import Queue
from typing import TypeVar, Type
from abc import ABC, abstractmethod

from backtest_env.dto import Args
from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet

T = TypeVar("T", bound="Strategy")


class Strategy(ABC):
    # base class for all strategies
    def __init__(self, args: Args):
        self.data = PriceDataSet(args.symbol, args.timeframe, args.startTime, args.endTime)
        self.position_manager = PositionManager(self.data, args.initialBalance)
        self.order_manager = OrderManager(self.position_manager, self.data)

    def run(self, event_queue: Queue):
        # strategy will: call self.data.step() to move forward to the next price
        # validate account's state: orders, positions,...
        # inspect new input data: prices, indicators,... from backend
        # determine the next action: submit buy/sell order, cancel orders, close positions, ...
        while self.data.step():
            event_queue.put(self.data.get_current_price().to_json())
            self.update()
        print("Backtest finished")

    @abstractmethod
    def update(self):
        pass

    @classmethod
    def from_cfg(cls: Type[T], kwargs):
        args = Args(**kwargs)
        return cls(args)

    @classmethod
    def get_required_params(cls: Type[T]) -> dict:
        return {}