from abc import ABC, abstractmethod
from enum import StrEnum
from uuid import uuid4

from backtest_env.base.side import OrderSide, PositionSide
from backtest_env.base.event_hub import EventHub


class OrderType(StrEnum):
    Market = "Market"
    Limit = "Limit"
    TakeProfit = "TakeProfit"
    Stoploss = "Stoploss"
    ClosePosition = "ClosePosition"
    OCO = "OCO"
    Stop = "Stop"

    def __str__(self):
        return self.value


class Order(ABC, EventHub):
    # common sense: limit buy 1.0 bnb at price = 500.0
    def __init__(
        self,
        side: OrderSide,
        amount_in_usd: float,
        symbol: str,
        price: float,
        position_side: PositionSide = None,
        created_at: int = 0,
        price_at_creation: float = -1.0,
    ):
        super().__init__()
        self.id = uuid4().hex[:16]
        self.type: str = ""
        self.side: OrderSide = side
        self.quantity: float = round(amount_in_usd / price, 4)
        self.symbol: str = symbol
        self.price: float = price
        self.position_side: PositionSide = position_side if position_side else side.to_position()
        self.created_at: int = created_at
        self.filled_at: int = -1
        self.price_at_creation: float = price_at_creation
        self.reasons: str = "" # reasons why we made this order

    @abstractmethod
    def update(self, price):
        pass

    def emit_order_filled(self, filled_at: int):
        self.filled_at = filled_at
        self.emit("order.filled", self)

    def __str__(self):
        return (
            f"{self.type} "
            f"{self.side} "
            f"{self.quantity} "
            f"{self.symbol} "
            f"at {self.price}, "
            f"position side = {self.position_side}"
        )

    def json(self):
        return {
            "type": self.type,
            "side": self.side,
            "quantity": self.quantity,
            "symbol": self.symbol,
            "price": self.price,
            "positionSide": self.position_side,
            "id": self.id,
            "createdAt": self.created_at // 1000,
            "filledAt": self.filled_at // 1000,
            "priceAtCreation": self.priceAtCreation,
        }
