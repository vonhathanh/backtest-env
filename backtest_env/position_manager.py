from backtest_env.position import Position


class PositionManager:
    def __init__(self):
        self.positions: dict[str, Position] = {}

    def fill(self, order):
        self.positions[order.id].fill(order)

    def get_positions(self):
        return self.positions