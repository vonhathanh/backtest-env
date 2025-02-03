from typing import Optional

from pydantic import BaseModel


class BacktestParam(BaseModel):
    test_id: int
    strategies: list[str]
    initial_balance: float
    symbol: str
    timeframe: str
    start_time: str
    end_time: Optional[str]