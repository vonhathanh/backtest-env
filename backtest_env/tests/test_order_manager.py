from unittest.mock import Mock

from backtest_env.order import Order, OrderType
from backtest_env.order_manager import OrderManager
from backtest_env.utils import get_random_string


class TestOrderManager:
    data = Mock()
    position_mgr = Mock()
    order_mgr = OrderManager(position_mgr, data)

    def test_split_orders_by_side(self):
        # empty orders
        long_orders, short_orders = self.order_mgr.split_orders_by_side()
        assert len(long_orders) == 0 and len(short_orders) == 0

        # 1 buy and 0 sell order
        self.order_mgr.add_order(Order(1.0, "BNBUSDT", "BUY", OrderType.Market, "", 1.0, get_random_string()))
        long_orders, short_orders = self.order_mgr.split_orders_by_side()
        assert len(long_orders) == 1 and len(short_orders) == 0

        # add new sell order
        self.order_mgr.add_order(Order(1.0, "BNBUSDT", "SELL", OrderType.Market, "", 1.0, get_random_string()))
        long_orders, short_orders = self.order_mgr.split_orders_by_side()
        assert len(long_orders) == 1 and len(short_orders) == 1

        # more than 1 sell order
        self.order_mgr.add_order(Order(1.0, "BNBUSDT", "SELL", OrderType.Market, "", 1.0, get_random_string()))
        long_orders, short_orders = self.order_mgr.split_orders_by_side()
        assert len(long_orders) == 1 and len(short_orders) == 2
