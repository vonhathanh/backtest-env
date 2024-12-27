from backtest_env.strategies import Baseline, TrendFollower
from backtest_env.utils import load_params


def main():
    params = load_params("../configs.json")
    # s = Baseline(params["Baseline"])
    # s.run()
    s = TrendFollower(params["TrendFollower"])
    s.run()

if __name__ == '__main__':
    main()