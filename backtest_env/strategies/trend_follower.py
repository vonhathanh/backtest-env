from backtest_env.strategies import Strategy


class TrendFollower(Strategy):
    """
    1) Open both long and short at daily candle close price
    2) Place limit long orders at the upper side of the entry price.
    3) Place limit short orders at the lower side of the entry price.
       Each long/short order has equal price difference with its predecessor/successor
    4) Price difference is the average 1h-4h candle's length
    5) To avoid complexity, we'll place 20 orders at both sides
    6) Close all positions/orders at the end of the next candle
    7) Test this one with highly volatile symbols
    8) Need an indicator/measure to know which pair is volatile
    """
    pass