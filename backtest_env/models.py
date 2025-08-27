from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

from backtest_env.base.side import OrderSide, PositionSide

class Order(SQLModel, table=True):
    id: int = Field(unique=True, primary_key=True)
    session_id: str
    side: OrderSide
    quantity: float
    symbol: str
    price: float
    position_side: Optional[PositionSide] = None
    created_at: datetime
    filled_at: Optional[datetime] = None
    price_at_creation: Optional[float] = None
    reasons: Optional[str] = None

