import numpy as np
from socketio import Client

from backtest_env.base_class.event_emitter import EventEmitter
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

    def json(self):
        return {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "time": self.close_time // 1000,
        }


class PriceDataSet(EventEmitter):
    def __init__(self, symbol, tf, start_time: str, end_time: str = "", sio: Client = None):
        super().__init__(sio)
        start = convert_datetime_to_nanosecond(start_time)
        end = convert_datetime_to_nanosecond(end_time)

        self.prices: np.ndarray = load_price_data(DATA_DIR, symbol, tf, start, end)
        self.idx = -1

    def get_current_price(self) -> Price:
        assert self.idx != -1
        return self[self.idx]

    def get_open_price(self):
        return self.get_current_price().open

    def get_close_price(self):
        return self.get_current_price().close

    def get_close_time(self):
        return self.get_current_price().close_time

    def get_last_price(self):
        return self[-1]

    def next(self) -> Price:
        return self[self.idx + 1]

    def step(self):
        self.idx += 1
        is_ended = self.idx >= len(self.prices)
        if not is_ended:
            self.emit("new_candle", self.get_current_price().json())
        return is_ended

    def __len__(self):
        return len(self.prices)

    def __getitem__(self, index: int):
        return Price(*self.prices[index]) if index < len(self.prices) else None
