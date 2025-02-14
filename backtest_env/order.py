import time
from enum import Enum
from uuid import uuid4

class OrderType(Enum):
    Market = 1,
    Limit = 2,
    TakeProfit = 3,
    Stoploss= 4

class Order:
    # common sense: limit buy 1.0 bnb at price = 500.0
    def __init__(self,
                 order_type: OrderType,
                 side: str,
                 quantity: float,
                 symbol: str,
                 price: float,
                 position_side: str,
                 order_id: str = ""):
        self.type = order_type
        self.side = side
        self.quantity = quantity
        self.symbol = symbol
        self.price = price
        self.position_side = position_side
        self.id = order_id if order_id else uuid4().hex
        self.created_at = int(time.time_ns())
