from dataclasses import dataclass


@dataclass
class Balance:
    initial: float
    current: float
    margin: float

    def get_pnl(self):
        return round(self.current - self.initial, 4)
