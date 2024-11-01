class Backend:

    pending_orders: list = []
    positions: list = []
    # available cash (in $)
    balance: float = 0.0

    def get_pending_orders(self) -> list:
        return self.pending_orders

    def get_positions(self) -> list:
        return self.positions

    def get_balance(self) -> float:
        return self.balance