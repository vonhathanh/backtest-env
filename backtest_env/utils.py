import json
import time
from typing import Any

import numpy as np

from os.path import join
from backtest_env.constants import *


def load_data(data_dir: str, symbol: str, tf: str, start: int, end: int) -> np.ndarray:
    file_name = join(data_dir, symbol + '_' + tf + '.csv')
    # use np.genfromtxt instead of pandas.read_csv so pandas is not a dependency
    data = np.genfromtxt(file_name, delimiter=',', skip_header=1)
    # filter data by start and end time
    # data must be in range of [start, end]
    end = np.inf if end == 0 else end # end's default value is zero, we have to increase it to np.inf if necessary
    mask = (data[:, 0] >= start) & (data[:, 0] <= end)

    return data[mask]


def load_params(config_file_path: str) -> dict[str, Any]:
    """
    load config from configs.json file into memory, result is a dictionary
    :param config_file_path: directory that store config file
    :return: configs dict
    """
    with open(config_file_path, "r") as f:
        configs = json.load(f)
    return configs

def get_sl(price: float, percent: float, side: str) -> float:
    """
    get stop-loss entry based on current price and pre-defined deviate percent
    :param price: entry price of the order
    :param percent: how many percent the stop-loss will be away from entry price
    :param side: current trading side of the parent order that we want to make SL for
    :return: entry price for stop-loss to be triggered
    """
    return price * (1 - percent) if side == "BUY" else price * (1 + percent)


def get_tp(price: float, percent: float, side: str) -> float:
    """
    get take-profit entry based on current price and pre-defined deviate percent
    :param price: entry price of the order
    :param percent: how many percent the take-profit will be away from entry price
    :param side: current trading side of the parent order that we want to make TP for
    :return: entry price for take-profit to be triggered
    """
    return price * (1 + percent) if side == "BUY" else price * (1 - percent)

def market_order(symbol: str, side: str, price: float, quantity: float) -> dict[str, Any]:
    """
    create market order (instant filled order)
    :param symbol: name of the trading pair: BNBUSDT, BTCUSDT...
    :param side: order side, can be: BUY, SELL
    :param price: entry price of the order
    :param quantity: how much token we want to buy/sell
    :return: dictionary contains all valid parameters for the server to fill the order for us
    """
    price = round_precision(price)
    quantity = round_precision(quantity)
    return {
        "price": price,
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "positionSide": to_position(side),
        "quantity": quantity,
        "id": f"{side}_{symbol}_{time.time()}",
    }

def round_precision(num: float) -> float:
    return num

def to_position(side: str) -> str:
    # convert order side to position side
    return LONG if side == BUY else SHORT
