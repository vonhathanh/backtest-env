from socketio import Client

from backtest_env.balance import Balance
from backtest_env.base_class.event_emitter import EventEmitter
from backtest_env.constants import LONG
from backtest_env.order import Order
from backtest_env.position import LongPosition, ShortPosition, Position


class PositionManager(EventEmitter):
    def __init__(self, initial_balance: float, sio: Client = None):
        super().__init__(sio)
        self.balance = Balance(initial_balance, initial_balance, 0)
        self.long = LongPosition(self.balance)
        self.short = ShortPosition(self.balance)

    def emit_positions(self):
        self.emit("positions", [pos.json() for pos in [self.long, self.short]])

    def emit_pnl(self, price: float):
        self.emit("pnl", self.get_pnl(price))

    def fill(self, order: Order):
        if order.position_side == LONG:
            self.long.update(order)
        else:
            self.short.update(order)
        self.emit_positions()

    def get_positions(self) -> tuple[Position, Position]:
        return self.long, self.short

    def get_total_active_positions(self) -> int:
        return self.long.is_active() + self.short.is_active()

    def get_unrealized_pnl(self, price: float) -> float:
        return round(self.long.get_pnl(price) + self.short.get_pnl(price), 4)

    def get_pnl(self, price: float):
        pnl = self.balance.get_pnl()
        # testing is not ended, so we must account for pnl of long & short position
        if price:
            pnl += self.long.value(price) + self.balance.margin - self.short.value(price)
        return pnl
