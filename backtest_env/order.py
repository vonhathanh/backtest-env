from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OrderType(Enum):
    Market = 1,
    Limit = 2,
    TakeProfit = 3,
    Stoploss= 4

@dataclass
class Order:
    price: Optional[float]
    symbol: str
    side: str
    type: OrderType
    positionSide: Optional[str]
    quantity: float
    id: str
