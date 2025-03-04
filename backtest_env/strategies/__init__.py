from backtest_env.strategies.baseline import Baseline
from backtest_env.strategies.trend_follower import TrendFollower

# Factory method design pattern
STRATEGIES = {
    "Baseline": Baseline,
    "TrendFollower": TrendFollower,
}
