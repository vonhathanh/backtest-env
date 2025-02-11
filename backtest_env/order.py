from enum import Enum
from uuid import uuid4

class OrderType(Enum):
    Market = 1,
    Limit = 2,
    TakeProfit = 3,
    Stoploss= 4

class Order:
    def __init__(self, price, symbol, side, order_type, position_side, quantity, id: str = ""):
        self.price = price
        self.symbol = symbol
        self.side = side
        self.type = order_type
        self.position_side = position_side
        self.quantity = quantity
        self.id = uuid4().hex if not id else id
