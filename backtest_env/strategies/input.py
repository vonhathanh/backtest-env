from dataclasses import dataclass

import numpy as np


@dataclass
class Input:
    prices: np.ndarray
    trading_history: list[dict] = None
    pending_orders: list[dict] = None
    positions: list[dict] = None
    indicator_data: list[dict] = None
