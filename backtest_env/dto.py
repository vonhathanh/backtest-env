from typing import Optional

from pydantic import BaseModel


class Args(BaseModel):
    initialBalance: float
    symbol: str
    timeframe: str
    startTime: str  # YYYY-mm-dd format
    endTime: Optional[str]  # YYYY-mm-dd format
    strategy: str


class TrendFollowerArgs(Args):
    gridSize: int
    orderSize: float
    interval: int
    candleCacheSize: int
