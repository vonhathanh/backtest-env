from backtest_env.strategies.baseline import Baseline
from backtest_env.strategies.strategy import Strategy
from backtest_env.strategies.trend_follower import TrendFollower
from backtest_env.strategies.websocket_strategy import WebsocketStrategy

# Factory method design pattern
STRATEGIES = {
    "Baseline": Baseline,
    "TrendFollower": TrendFollower,
}