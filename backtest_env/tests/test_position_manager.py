from unittest.mock import Mock

from backtest_env.constants import BUY, LONG, SHORT, SELL
from backtest_env.order import Order, OrderType
from backtest_env.position_manager import PositionManager


class TestPositionManager:

    def setup_method(self):
        self.data = Mock()
        self.initial_balance = 10000.0
        self.position_mgr = PositionManager(self.data, self.initial_balance)

    def test_fill_long_order(self):
        order = Order(500.0, "BNB", BUY, OrderType.Market, LONG, 1.0)
        self.position_mgr.fill(order)

        assert self.position_mgr.balance == self.initial_balance - 500.0

    def test_fill_short_order(self):
        order = Order(250.0, "BTC", SELL, OrderType.Market, SHORT, 0.5)
        self.position_mgr.fill(order)

        assert self.position_mgr.balance == self.initial_balance
        assert self.position_mgr.margin == 125

    def test_get_number_of_active_positions(self):
        assert self.position_mgr.get_number_of_active_positions() == 0

        self.position_mgr.long.quantity += 1.0
        assert self.position_mgr.get_number_of_active_positions() == 1

        self.position_mgr.short.quantity += 1.0
        assert self.position_mgr.get_number_of_active_positions() == 2

    def test_close_long_position(self):
        order = Order(500.0, "BNB", BUY, OrderType.Market, LONG, 1.0)
        self.position_mgr.fill(order)

        # close long position at price = 300
        self.data.get_open_price.return_value = 300.0
        self.position_mgr.close()

        assert self.position_mgr.long.quantity == 0.0
        assert self.position_mgr.long.avg_price == 0.0
        assert self.position_mgr.balance == self.initial_balance - 200

    def test_close_short_position(self):
        order = Order(500.0, "BNB", SELL, OrderType.Market, SHORT, 1.0)
        self.position_mgr.fill(order)

        # close long position at price = 300
        self.data.get_open_price.return_value = 300.0
        self.position_mgr.close()

        assert self.position_mgr.short.quantity == 0.0
        assert self.position_mgr.short.avg_price == 0.0
        assert self.position_mgr.balance == self.initial_balance + 200