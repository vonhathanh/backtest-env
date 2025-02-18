from typing import Optional, Any

from pydantic import BaseModel

class Args(BaseModel):
    initialBalance: float
    symbol: str
    timeframe: str
    startTime: str
    endTime: Optional[str]

class TrendFollowerArgs(Args):
    gridSize: int
    orderSize: float
    interval: int
    candleCacheSize: int

class BacktestConfig(BaseModel):
    strategies: list[Any]
    generalConfig: Args


