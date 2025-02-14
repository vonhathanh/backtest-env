from typing import Optional

from pydantic import BaseModel

class Args(BaseModel):
    initial_balance: float
    symbol: str
    timeframe: str
    start_time: str
    end_time: Optional[str]

class TrendFollowerArgs(Args):
    grid_size: int
    order_size: float

class BacktestParam(Args):
    strategies: list[str]


