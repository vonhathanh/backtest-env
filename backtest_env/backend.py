from dataclasses import dataclass

@dataclass
class Position:
    long: float = 0.0
    short: float = 0.0

    def __len__(self):
        return 1 - (self.long == 0) + 1 - (self.short == 0)

class Backend:
    # dictionary where key is order id and value is the order parameter
    pending_orders: dict[str, dict] = {}
    position: Position = Position(0, 0)
    # available cash (in $)
    balance: float = 0.0

    def add_orders(self, orders: list):
        for order in orders:
            self.pending_orders[order["id"]] = order

    def remove_order(self, order: dict):
        del self.pending_orders[order["id"]]

    def cancel_all_pending_orders(self):
        for order_id in self.pending_orders.keys():
            self.cancel_order(order_id)

    def cancel_order(self, order_id):
        # in reality, call OrderDispatcher.cancel()
        del self.pending_orders[order_id]

    def close_all_positions(self):
        pass

    def get_pending_orders(self) -> dict:
        return self.pending_orders

    def get_positions(self) -> Position:
        return self.position

    def get_balance(self) -> float:
        return self.balance

    def get_prices(self, size: int = 1):
        pass

    def get_total_wealth(self, price: float):
        return self.balance + self.position.long * price - self.position.short * price
