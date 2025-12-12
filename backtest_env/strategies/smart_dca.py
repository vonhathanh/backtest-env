from backtest_env.base.strategy import Strategy


class SmartDCA(Strategy):
    # start: buy X amount of symbol Y at price P
    # set TP at P*1.1
    # when P = P*0.9 do:
    # sell 0.1X
    # short 0.1X
    # when P = P*0.8 do:
    # close short
    # buy back 0.1X
    pass