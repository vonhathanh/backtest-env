from backtest_env.base.strategy import Strategy
from backtest_env.dto import Args


class RuleBasedAdaptiveAgent(Strategy):
    """
    1) A simple buy low, sell high strategy with 3 main parameters
        - entry_ratio
        - split_count
        - tp/sl_ratio
    2) Each order will have fixed size
    3) We'll update tp and sl based on statistics of previous orders and candlestick data
    4) Update algorithm:
        - Initialize tp and sl to 1/3 of order size
        - But aren't we are training a ML to fit these data?
        - yes, this is a rudimentary form of ML
    5) two versions: trail SL and non-trail SL
    """

    def __init__(self, args: Args):
        super().__init__(args)

    def update(self):
        self.update_parameters()

    def update_parameters(self):
        self.update_entry_ratio()
        self.update_split_count()
        self.update_tp_ratio()

    def update_entry_ratio():
        """
        Store order history that includes:
        - Order creation time
        - Current price at order creation
        - Current entry_ratio at that time
        - Time between order filled time vs creation time
        - profit and loss when order is finished
        Order evaluation's criterias:
        - Small time to reach the entry price
        - Number of TPs hit is > number of SLs
        - If a position is not winning/losing, it's not a good order.
        - Entry + TP should be based on recent average price change
        - Time it took to price to reach the order's entry point. If its too long, reduce entry_ratio
        - Time it took to reach all TPs. If its too long, increase entry_ratio + reduce tp_ratio
        - If No. candle is + profit/loss are both small -> good entry ratio else update it
        - If No. candle is big + profit/loss is small -> good but might not be the best, go back in history to see if we can find a better entry
        - If No. candle is small + profit/loss is big -> increase ratio
        - If No. candle is big + profit/loss is big -> increase ratio at larger magnitude
        """
        pass

    def update_split_count():
        pass

    def update_tp_ratio():
        pass
