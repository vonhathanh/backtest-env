import time
from enum import Enum
from uuid import uuid4


class OrderType(Enum):
    Market = 1,
    Limit = 2,
    TakeProfit = 3,
    Stoploss = 4


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
        self.id = order_id if order_id else uuid4().hex[:16]
        self.created_at = int(time.time_ns())

    def __str__(self):
        return (f"{self.type} "
                f"{self.side} "
                f"{self.quantity} "
                f"{self.symbol} "
                f"at {self.price}, "
                f"position side = {self.position_side}")

    def json(self):
        return {
            "side": self.side,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "price": self.price,
            "positionSide": self.position_side,
            "id": self.id,
            "createdAt": self.created_at
        }
