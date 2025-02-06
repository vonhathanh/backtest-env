from typing import Optional

from pydantic import BaseModel


class BacktestParam(BaseModel):
    strategies: list[str]
    initial_balance: float
    symbol: str
    timeframe: str
    start_time: str
    end_time: Optional[str]

class TrendFollowerParam(BacktestParam):
    grid_size: int
    order_size: float
