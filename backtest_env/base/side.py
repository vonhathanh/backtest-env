from enum import StrEnum


class OrderSide(StrEnum):
    BUY = "Buy"
    SELL = "Sell"

    def reverse(self):
        return OrderSide.BUY if self == OrderSide.SELL else OrderSide.SELL

    def to_position(self):
        return PositionSide.LONG if self == OrderSide.BUY else PositionSide.SHORT


class PositionSide(StrEnum):
    LONG = "Long"
    SHORT = "Short"

    def reverse(self):
        return PositionSide.LONG if self == PositionSide.SHORT else PositionSide.SHORT
