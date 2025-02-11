from unittest.mock import Mock

from backtest_env.order import Order, OrderType
from backtest_env.order_manager import OrderManager
from backtest_env.price import Price
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

    def test_process_orders(self):
        market_order = Order(100.0, "BNBUSDT", "BUY", OrderType.Market, "", 1.0, get_random_string())
        limit_order = Order(120.0, "BNBUSDT", "BUY", OrderType.Limit, "", 1.0, get_random_string())

        self.order_mgr.add_orders([market_order, limit_order])

        # force price to return 100 so limit order not filled
        self.order_mgr.data.get_current_price.return_value = Price(0, 100, 100, 100, 100, 0)

        # process only market order so limit order will stay
        self.order_mgr.process_orders()
        orders = self.order_mgr.get_orders()
        assert len(orders) == 1 and orders[0].type == OrderType.Limit

