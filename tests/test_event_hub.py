from unittest.mock import Mock

import pytest

from backtest_env.order_manager import OrderManager
from tests.test_position_manager import price
from utils import create_long_order


class TestEventHub:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = Mock()
        self.position_mgr = Mock()
        self.order_mgr = OrderManager(self.position_mgr, self.data)
        yield
        # Teardown code
        self.order_mgr.unsubscribe()
        self.order_mgr = None
        self.position_mgr = None
        self.data = None


    def test_on_order_filled(self):
        self.order_mgr.add_order(create_long_order(price=500.0))

        self.data.get_current_price.return_value = price(close=500)
        self.order_mgr.process_orders()
        assert len(self.order_mgr.get_all_orders()) == 0
        assert len(self.order_mgr.get_order_history()) == 1
