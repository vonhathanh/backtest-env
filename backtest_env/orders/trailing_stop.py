from backtest_env.base.order import Order
from backtest_env.price import Price


class TrailingStop(Order):
    def update(self, price: Price):
        pass
