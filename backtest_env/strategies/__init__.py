from backtest_env.strategies.baseline import Baseline
from backtest_env.strategies.strategy import Strategy
from backtest_env.strategies.trend_follower import TrendFollower

STRATEGIES = {
    "Base": Strategy,
    "Baseline": Baseline,
    "TrendFollower": TrendFollower,
}