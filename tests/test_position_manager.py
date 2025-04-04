from math import isclose
from unittest.mock import Mock

import pytest

from backtest_env.order_manager import OrderManager
from backtest_env.position_manager import PositionManager
from backtest_env.price import Price
from backtest_env.base.order import OrderSide
from utils import create_long_order, create_short_order


def price(open_price=0.0, high=0.0, low=0.0, close=0.0, close_time=0) -> Price:
    return Price(0, open_price, high, low, close, close_time)


class TestPositionManager:
    initial_balance = 10000.0

    @pytest.fixture(autouse=True)
    def setup(self):
        self.dataset = Mock()
        self.position_mgr = PositionManager(self.initial_balance)
        self.order_mgr = OrderManager(self.position_mgr, self.dataset)
        yield
        # Teardown code
        self.order_mgr.unsubscribe()
        self.order_mgr = None
        self.position_mgr = None
        self.dataset = None

    def get_current_balance(self):
        return self.position_mgr.balance.current

    def get_current_margin(self):
        return self.position_mgr.balance.margin

    def long(self):
        return self.position_mgr.long

    def short(self):
        return self.position_mgr.short

    def get_unrealized_pnl(self, current_price: float):
        return self.position_mgr.get_unrealized_pnl(current_price)

    def test_fill_long_order(self):
        self.position_mgr.fill(create_long_order(price=500.0))
        assert self.get_current_balance() == self.initial_balance - 500.0

    def test_fill_short_order(self):
        self.position_mgr.fill(create_short_order(price=250.0, quantity=0.5))

        assert self.get_current_balance() == self.initial_balance
        assert self.get_current_margin() == 250 * 0.5

    def test_get_number_of_active_positions(self):
        assert self.position_mgr.get_total_active_positions() == 0

        self.long().quantity += 1.0
        assert self.position_mgr.get_total_active_positions() == 1

        self.short().quantity += 1.0
        assert self.position_mgr.get_total_active_positions() == 2

    def test_close_long_position(self):
        self.order_mgr.add_order(create_long_order(price=500.0))

        self.dataset.get_current_price.return_value = price(close=500)
        self.order_mgr.process_orders()

        self.dataset.get_current_price.return_value = price(close=300)
        self.order_mgr.close_all_positions(price(close=300.0))

        assert self.long().quantity == 0.0
        assert self.long().average_price == 0.0
        assert self.get_current_balance() == self.initial_balance - 200

    def test_close_short_position(self):
        self.order_mgr.add_order(create_short_order(price=500.0))

        self.dataset.get_current_price.return_value = price(close=500)
        self.order_mgr.process_orders()

        self.order_mgr.close_all_positions(price(close=300.0))

        assert self.short().quantity == 0.0
        assert self.short().average_price == 0.0
        assert self.get_current_balance() == self.initial_balance + 200

    @pytest.mark.parametrize("quantity", [0.5, 0.75, 1.0, 1.25])
    def test_long_unrealized_pnl_at_different_quantities(self, quantity):
        start_price, next_price, last_price = 123.45, 333.12, 100.12

        self.order_mgr.add_order(create_long_order(price=start_price, quantity=quantity))
        self.dataset.get_current_price.return_value = price(close=start_price)
        self.order_mgr.process_orders()

        assert isclose(self.get_unrealized_pnl(next_price), (next_price - start_price) * quantity)
        assert isclose(self.get_unrealized_pnl(last_price), (last_price - start_price) * quantity)

    def test_long_unrealized_pnl_at_different_prices(self):
        start_price, next_price, delta = 123.45, 333.12, 100.0
        self.position_mgr.fill(create_long_order(price=start_price))

        # fill another order at next_price, expect pnl only account by the first trade
        self.position_mgr.fill(create_long_order(price=next_price))
        assert isclose(self.get_unrealized_pnl(next_price), (next_price - start_price))
        # price goes down by delta
        assert isclose(
            self.position_mgr.get_unrealized_pnl(next_price - delta),
            next_price - start_price - delta * self.long().quantity,
        )

    def test_get_short_unrealized_pnl(self):
        self.position_mgr.fill(create_short_order(price=200.0))
        assert self.position_mgr.get_unrealized_pnl(300.5) == round(-100.5, 4)
        assert self.position_mgr.get_unrealized_pnl(155.3) == round(200 - 155.3, 4)

        # fill another order at the same current price, expect pnl unchanged
        self.position_mgr.fill(create_short_order(price=300.5))
        assert self.position_mgr.get_unrealized_pnl(300.5) == round(-100.5, 4)

        # price goes down by 100, our profit is increased by 2*100
        assert self.position_mgr.get_unrealized_pnl(200.5) == round(-100.5 + 200, 4)

        # reduce position by 0.5, pnl is reduced
        self.position_mgr.fill(create_short_order(price=200.5, quantity=0.5, side=OrderSide.BUY))
        assert self.position_mgr.get_unrealized_pnl(200.5) == round((250.25 - 200.5) * 1.5, 4)

    def test_get_unrealized_pnl_with_both_long_and_short(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=250.0, quantity=0.5))
        assert self.position_mgr.get_unrealized_pnl(300) == 75.0

    def test_long_and_short_neutralized_each_other(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=200.0))
        assert self.position_mgr.get_unrealized_pnl(200.0) == 0.0

        self.order_mgr.close_all_positions(price(close=300.0))
        assert self.position_mgr.get_pnl(0.0) == 0

    def test_buy_low_sell_high(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=300.0))
        # price is not important as we buy low and sell high
        assert self.position_mgr.get_unrealized_pnl(220) == 100.0
        assert self.position_mgr.get_unrealized_pnl(280) == 100.0

        self.order_mgr.close_all_positions(price(close=300.0))
        assert self.position_mgr.get_pnl(0.0) == 100.0

    def test_long_pnl(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.order_mgr.close_all_positions(price(close=123.45))
        assert self.position_mgr.get_pnl(0.0) == round(123.45 - 200, 4)

        self.position_mgr.fill(create_long_order(price=200.0))
        self.order_mgr.close_all_positions(price(close=321.44))
        assert self.position_mgr.get_pnl(0.0) == round(-76.55 + 321.44 - 200.0, 4)

    def test_short_pnl(self):
        self.position_mgr.fill(create_short_order(price=300.0))
        self.order_mgr.close_all_positions(price(close=123.45))
        assert self.position_mgr.get_pnl(0.0) == round(300 - 123.45, 4)

        self.position_mgr.fill(create_short_order(price=123.45))
        self.order_mgr.close_all_positions(price(close=200.0))
        assert self.position_mgr.get_pnl(0.0) == round(300 - 200, 4)

    def test_long_and_short_pnl(self):
        self.position_mgr.fill(create_short_order(price=300.0))
        self.position_mgr.fill(create_long_order(price=200.0, quantity=0.5))
        # pnl += 25.0
        self.position_mgr.fill(create_short_order(price=250.0, side=OrderSide.BUY, quantity=0.5))
        self.order_mgr.close_all_positions(price(close=225.0))
        # 0.5 short at 300, pnl += 37.5
        # 0.5 long at 200, pnl += 12.5
        assert self.position_mgr.get_pnl(0.0) == 37.5 + 25 + 12.5
