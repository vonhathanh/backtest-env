import json


def load_params(config_file_path: str):
    with open(config_file_path, "r") as f:
        configs = json.load(f)
        print(configs)
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

def market_order(symbol: str, side: str, price: float, quantity: float):
    price = round_precision(price)
    quantity = round_precision(quantity)
    return {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "positionSide": side,
        "quantity": quantity,
        "newClientOrderId": f"{side}_{symbol}",
    }

def round_precision(num: float) -> float:
    return num
