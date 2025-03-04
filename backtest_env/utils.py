import asyncio
import numpy as np

from datetime import datetime
from os.path import join

from backtest_env.constants import BUY, SELL, LONG, SHORT, DATA_DIR
from backtest_env.order import Order, OrderType


def create_long_order(
    order_type: OrderType = OrderType.Market,
    side: str = BUY,
    quantity=1.0,
    symbol: str = "X",
    price: float = 100.0,
    position_side: str = LONG,
):
    return Order(order_type, side, quantity, symbol, price, position_side)


def create_short_order(
    order_type: OrderType = OrderType.Market,
    side: str = SELL,
    quantity=1.0,
    symbol: str = "X",
    price: float = 100.0,
    position_side: str = SHORT,
):
    return Order(order_type, side, quantity, symbol, price, position_side)


def load_price_data(
    data_dir: str, symbol: str, tf: str, start: int, end: int = 0
) -> np.ndarray:
    file_name = join(data_dir, symbol + "_" + tf + ".csv")
    # use np.genfromtxt instead of pandas.read_csv so pandas is not a dependency
    data = np.genfromtxt(file_name, delimiter=",", skip_header=1)
    # filter data by start and end time
    # data must be in range of [start, end]
    end = (
        np.inf if end == 0 else end
    )  # end's default value is zero, we have to increase it to np.inf if necessary
    mask = (data[:, 0] >= start) & (data[:, 0] <= end)

    return data[mask]


def get_sl(price: float, percent: float, side: str) -> float:
    """
    get stop-loss entry based on current price and pre-defined deviate percent
    :param price: entry price of the order
    :param percent: how many percent the stop-loss will be away from entry price
    :param side: current trading side of the parent order that we want to make SL for
    :return: entry price for stop-loss to be triggered
    """
    return round(price * (1 - percent) if side == "BUY" else price * (1 + percent), 4)


def get_tp(price: float, percent: float, side: str) -> float:
    """
    get take-profit entry based on current price and pre-defined deviate percent
    :param price: entry price of the order
    :param percent: how many percent the take-profit will be away from entry price
    :param side: current trading side of the parent order that we want to make TP for
    :return: entry price for take-profit to be triggered
    """
    return round(price * (1 + percent) if side == "BUY" else price * (1 - percent), 4)


def to_position(side: str) -> str:
    # convert order side to position side
    return LONG if side == BUY else SHORT


def convert_datetime_to_nanosecond(date: str, date_format: str = "%Y-%m-%d") -> int:
    return int(datetime.strptime(date, date_format).timestamp()) * 1000


def convert_nanosecond_to_datetime(nanosecond: int | float) -> str:
    return datetime.fromtimestamp(nanosecond // 1000).strftime("%Y-%m-%d")


def extract_metadata_from_file(name: str):
    # remove .csv suffix by :-4
    symbol, tf = name[:-4].split("_")

    data = np.genfromtxt(join(DATA_DIR, name), delimiter=",", skip_header=1)
    start_time = convert_nanosecond_to_datetime(data[0, 0])
    end_time = convert_nanosecond_to_datetime(data[-1, 0])

    return {"start_time": start_time, "end_time": end_time, "symbol": symbol, "tf": tf}


async def extract_metadata_in_batch(filenames: list[str]):
    return await asyncio.gather(
        *(asyncio.to_thread(extract_metadata_from_file, name) for name in filenames)
    )
