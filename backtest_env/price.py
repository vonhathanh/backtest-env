from dataclasses import dataclass

import numpy as np

from backtest_env.utils import load_data


@dataclass
class Price:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    close_time: float

class PriceData:
    def __init__(self, params: dict):
        data_dir, symbol, tf, start, end = (params["data_dir"],
                                            params["symbol"],
                                            params["tf"],
                                            params["start"],
                                            params["end"])
        self.prices: np.ndarray = load_data(data_dir, symbol, tf, start, end)
        self.idx = 0

    def get_current_price(self) -> Price:
        return Price(*self[self.idx])

    def get_open_price(self):
        return self.get_current_price().open

    def get_close_price(self):
        return self.get_current_price().close

    def step(self):
        self.idx += 1
        return self.idx < len(self.prices)

    def __len__(self):
        return len(self.prices)

    def __getitem__(self, item):
        return self.prices[item]

    # def get_prices(self, size: int = 1) -> np.ndarray | float:
    #     size = min(self.cur_idx, size)
    #     return self.data[self.cur_idx - size:self.cur_idx] if size > 1 else self.data[self.cur_idx]
    #
    # def get_last_close_price(self) -> float:
    #     return self.data[self.cur_idx][4]
    #
    # def get_last_open_price(self) -> float:
    #     return self.data[self.cur_idx][1]