import time
from enum import Enum
from uuid import uuid4


class OrderType(Enum):
    Market = "Market"
    Limit = "Limit"
    TakeProfit = "TakeProfit"
    Stoploss = "Stoploss"
    ClosePosition = "ClosePosition"

    def __str__(self):
        return self.value


class Order:
    # common sense: limit buy 1.0 bnb at price = 500.0
    def __init__(
        self,
        order_type: OrderType,
        side: str,
        quantity: float,
        symbol: str,
        price: float,
        position_side: str,
        created_at: int = int(time.time()),
    ):
        self.id = uuid4().hex[:16]
        self.type = order_type
        self.side = side
        self.quantity = quantity
        self.symbol = symbol
        self.price = price
        self.position_side = position_side
        self.created_at = created_at
        self.filled_at = -1

    def __str__(self):
        return (
            f"{self.type} "
            f"{self.side} "
            f"{self.quantity} "
            f"{self.symbol} "
            f"at {self.price}, "
            f"position side = {self.position_side}"
        )

    def json(self):
        return {
            "type": str(self.type),
            "side": self.side,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "price": self.price,
            "positionSide": self.position_side,
            "id": self.id,
            "createdAt": self.created_at // 1000,
            "filledAt": self.filled_at // 1000,
        }
