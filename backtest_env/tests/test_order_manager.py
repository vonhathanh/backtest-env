from unittest.mock import Mock

from backtest_env.order import Order, OrderType
from backtest_env.order_manager import OrderManager
from backtest_env.price import Price
from backtest_env.constants import LONG, BUY, SELL
from backtest_env.utils import create_long_order


class TestOrderManager:
    data = Mock()
    position_mgr = Mock()
    order_mgr = OrderManager(position_mgr, data)

    def test_get_open_orders(self):
        # empty orders
        orders = self.order_mgr.get_open_orders(BUY)
        assert len(orders) == 0

        # 1 buy and 0 sell order
        self.order_mgr.add_order(create_long_order(side=BUY))
        long_orders = self.order_mgr.get_open_orders(BUY)
        short_orders = self.order_mgr.get_open_orders(SELL)
        assert len(long_orders) == 1 and len(short_orders) == 0

        # add new sell order
        self.order_mgr.add_order(create_long_order(side=SELL))
        short_orders = self.order_mgr.get_open_orders(SELL)
        assert len(long_orders) == 1 and len(short_orders) == 1

        # more than 1 sell order
        self.order_mgr.add_order(create_long_order(side=SELL))
        short_orders = self.order_mgr.get_open_orders(SELL)
        assert len(long_orders) == 1 and len(short_orders) == 2

    def test_process_orders(self):
        market_order = create_long_order(side=BUY, price=100.0)
        limit_order = Order(OrderType.Limit, BUY, 1.0, "X", 120.0, LONG)

        self.order_mgr.add_orders([market_order, limit_order])

        # force price to return 100 so limit order not filled
        self.order_mgr.price_dataset.get_current_price.return_value = Price(0, 100, 100, 100, 100, 0)

        # process only market order so limit order will stay
        self.order_mgr.process_orders()
        orders = self.order_mgr.get_orders()
        assert len(orders) == 1 and orders[0].type == OrderType.Limit

        # force price to contain limit order price, so it can be processed
        self.order_mgr.price_dataset.get_current_price.return_value = Price(0, 110, 120, 100, 110, 0)

        self.order_mgr.process_orders()
        assert len(self.order_mgr.get_orders()) == 0

