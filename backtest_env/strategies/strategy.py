from typing import TypeVar, Type

T = TypeVar("T", bound="Strategy")

class Strategy:
    # base class for all strategies
    # contains logics to enter/exit trades
    def __init__(self, params: dict = None):
        pass

    def run(self, data: dict):
        # validate agent's state: orders, positions,...
        # inspect new input data: prices, indicators,...
        # create orders if necessary
        pass

    @classmethod
    def from_cfg(cls: Type[T], params):
        return cls(params)