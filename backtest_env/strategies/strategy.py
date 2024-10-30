from typing import TypeVar, Type

T = TypeVar("T", bound="Strategy")

class Strategy:
    # base class for all strategies
    # contains logics to enter/exit trades, close positions
    def __init__(self, params: dict = None):
        pass

    def run(self, data: dict):
        # validate agent's state: orders, positions,...
        # inspect new input data: prices, indicators,...
        # create orders if necessary
        # order can be normal buy/sell order or a special action such as cancel orders, close positions
        pass

    @classmethod
    def from_cfg(cls: Type[T], params):
        return cls(params)