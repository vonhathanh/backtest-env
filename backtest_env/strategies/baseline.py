from backtest_env.strategies.strategy import Strategy


class Baseline(Strategy):
    # base class for all strategies
    # contains logics to enter/exit trades
    def __init__(self):
        super().__init__()

    def run(self, data):
        super().run(data)