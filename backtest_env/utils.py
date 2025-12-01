import asyncio
import os

import numpy as np

from datetime import datetime
from os.path import join

from backtest_env.constants import DATA_DIR


def load_price_data(data_dir: str, symbol: str, tf: str, start: int, end: int = 0) -> np.ndarray:
    file_name = join(data_dir, symbol + "_" + tf + ".csv")
    # use np.genfromtxt instead of pandas.read_csv so pandas is not a dependency
    data = np.genfromtxt(file_name, delimiter=",", skip_header=1)
    # filter data by start and end time
    # data must be in range of [start, end]
    # end's default value is zero, we have to increase it to np.inf if necessary
    end = np.inf if end == 0 else end
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
    return round(price * (1 - percent) if side == "Buy" else price * (1 + percent), 4)


def get_tp(price: float, percent: float, side: str) -> float:
    """
    get take-profit entry based on current price and pre-defined deviate percent
    :param price: entry price of the order
    :param percent: how many percent the take-profit will be away from entry price
    :param side: current trading side of the parent order that we want to make TP for
    :return: entry price for take-profit to be triggered
    """
    return round(price * (1 + percent) if side == "Buy" else price * (1 - percent), 4)


def convert_datetime_to_nanosecond(date: str, date_format: str = "%Y-%m-%d") -> int:
    return int(datetime.strptime(date, date_format).timestamp()) * 1000


def convert_nanosecond_to_datetime(nanosecond: int | float) -> str:
    return datetime.fromtimestamp(nanosecond // 1000).strftime("%Y-%m-%d")


def extract_metadata_from_file(name: str):
    # remove .csv suffix by :-4
    tokens = name[:-4].split("_")
    symbol, tf = tokens[0], tokens[1]

    # filename contains start_time and end_time data
    if len(tokens) == 4:
        start_time = tokens[2]
        end_time = tokens[3]
    else: 
        # find start_time, end_time manually by reading the file and cache that information
        # to filename
        full_path = join(DATA_DIR, name)

        data = np.genfromtxt(full_path, delimiter=",", skip_header=1)
        
        start_time = convert_nanosecond_to_datetime(data[0, 0])
        end_time = convert_nanosecond_to_datetime(data[-1, 0])

        os.rename(full_path, join(DATA_DIR, f"{symbol}_{tf}_{start_time}_{end_time}.csv"))

    return {"start_time": start_time, "end_time": end_time, "symbol": symbol, "tf": tf}


async def extract_metadata_in_batch(filenames: list[str]):
    return await asyncio.gather(
        *(asyncio.to_thread(extract_metadata_from_file, name) for name in filenames)
    )
