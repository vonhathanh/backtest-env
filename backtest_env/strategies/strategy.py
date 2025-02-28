from typing import TypeVar, Type
from abc import ABC, abstractmethod

from backtest_env.dto import Args
from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import PriceDataSet
from backtest_env.logger import logger

T = TypeVar("T", bound="Strategy")


class Strategy(ABC):
    # base class for all strategies
    def __init__(self, args: Args):
        self.data = PriceDataSet(args.symbol, args.timeframe, args.startTime, args.endTime)
        self.position_manager = PositionManager(self.data, args.initialBalance)
        self.order_manager = OrderManager(self.position_manager, self.data)

    def run(self):
        # main event loop: getting new candle stick and then process data based on update() logic
        # child class must override update() to specify their own trading logic
        while self.data.step():
            self.update()
        self.cleanup()
        self.report()


    @abstractmethod
    def update(self):
        # validate account's state: orders, positions,...
        # inspect new input data: prices, indicators,... from other sources
        # determine the next action: submit buy/sell order, cancel orders, close positions, ...
        pass

    def cleanup(self):
        self.order_manager.cancel_all_orders()
        self.position_manager.close_all_positions()

    def report(self):
        logger.info(f"Backtest finished, pnl: {self.position_manager.get_pnl()}")

    @classmethod
    def from_cfg(cls: Type[T], kwargs):
        # Factory method design pattern, each subclass of Strategy decide the kwargs they want to initialize
        # read TrendFollower from_cfg() for example
        args = Args(**kwargs)
        return cls(args)

    @classmethod
    def get_required_params(cls: Type[T]) -> dict:
        # similar to from_cfg(), subclass might have other required params, and they can specify them here
        return {}