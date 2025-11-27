from unittest.mock import Mock

import pytest

from backtest_env.base.event_hub import Event, EventHub
from backtest_env.order_manager import OrderManager
from tests.test_position_manager import price
from utils import create_long_order


class TestEventHub:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = Mock()
        self.position_mgr = Mock()
        self.order_mgr = OrderManager(self.position_mgr, self.data)
        self.counter = 0
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

    def increase_counter(self, e: Event):
        self.counter += e.data

    def test_multiple_subscribers(self):
        hub1 = EventHub()
        hub2 = EventHub()
        hub3 = EventHub()
        hub1.subscribe('add', self.increase_counter)
        hub2.subscribe('add', self.increase_counter)

        hub3.emit('add', 3)

        assert self.counter == 6

    def test_unsubscribe(self):
        hub1 = EventHub()
        hub1.subscribe('add', self.increase_counter)
        hub1.emit('add', 3)

        assert self.counter == 3

        hub1.unsubscribe()
        
        hub1.emit('add', 3)
        assert self.counter == 3
        