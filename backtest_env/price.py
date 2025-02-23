from dataclasses import dataclass

import numpy as np

from backtest_env.constants import DATA_DIR
from backtest_env.utils import load_price_data, convert_datetime_to_nanosecond


class Price:

    def __init__(self, open_time, open_price, high, low, close, close_time):
        self.open_time = int(open_time)
        self.open = float(open_price)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.close_time = int(close_time)


    def to_json(self):
        return {
            "open_time": self.open_time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "close_time": self.close_time,
        }


class PriceDataSet:

    def __init__(self, symbol, tf, start_time: str, end_time: str = ""):
        start = convert_datetime_to_nanosecond(start_time)
        end = convert_datetime_to_nanosecond(end_time)

        self.prices: np.ndarray = load_price_data(DATA_DIR, symbol, tf, start, end)
        self.idx = -1

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
