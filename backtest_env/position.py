from backtest_env.order import Order


class Position:

    def __init__(self, side: str):
        self.side = side
        self.quantity = 0.0
        self.avg_price = 0.0

    def close(self):
        self.quantity = 0.0
        self.avg_price = 0.0

    # TODO: test get_pnl()
    def get_pnl(self, price: float) -> float:
        return self.quantity * (price - self.avg_price)

    # TODO: test update()
    def update(self, order: Order):
        assert order.quantity > 0.0
        self.avg_price = ((self.quantity * self.avg_price + order.quantity * order.price) /
                          (self.quantity + order.quantity))
        self.quantity += order.quantity