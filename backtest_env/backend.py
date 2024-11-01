class Position:
    long: float = 0.0
    short: float = 0.0

    def __len__(self):
        return 1 - (self.long == 0) + 1 - (self.short == 0)

class Backend:

    pending_orders: list = []
    position: Position
    # available cash (in $)
    balance: float = 0.0

    def get_pending_orders(self) -> list:
        return self.pending_orders

    def get_positions(self) -> Position:
        return self.position

    def get_balance(self) -> float:
        return self.balance

    def add_orders(self, orders: list):
        self.pending_orders += orders

    def get_prices(self, size: int=1):
        pass