from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import Field


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
    id: str = Field(default_factory=lambda: str(uuid4()))
