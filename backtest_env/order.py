from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    price: Optional[float]
    symbol: str
    side: str
    type: str
    positionSide: Optional[str]
    quantity: float
    id: str