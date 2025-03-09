from backtest_env.constants import SELL, BUY
from backtest_env.position_manager import PositionManager
from backtest_env.utils import create_long_order, create_short_order


class TestPositionManager:
    def setup_method(self):
        self.initial_balance = 10000.0
        self.position_mgr = PositionManager(self.initial_balance)

    def test_fill_long_order(self):
        self.position_mgr.fill(create_long_order(price=500.0))
        assert self.position_mgr.balance == self.initial_balance - 500.0

    def test_fill_short_order(self):
        self.position_mgr.fill(create_short_order(price=250.0, quantity=0.5))

        assert self.position_mgr.balance == self.initial_balance
        assert self.position_mgr.margin == 125

    def test_get_number_of_active_positions(self):
        assert self.position_mgr.get_number_of_active_positions() == 0

        self.position_mgr.long.quantity += 1.0
        assert self.position_mgr.get_number_of_active_positions() == 1

        self.position_mgr.short.quantity += 1.0
        assert self.position_mgr.get_number_of_active_positions() == 2

    def test_close_long_position(self):
        self.position_mgr.fill(create_long_order(price=500.0))
        self.position_mgr.close_all_positions(300.0)

        assert self.position_mgr.long.quantity == 0.0
        assert self.position_mgr.long.average_price == 0.0
        assert self.position_mgr.balance == self.initial_balance - 200

    def test_close_short_position(self):
        self.position_mgr.fill(create_short_order(price=500.0))
        self.position_mgr.close_all_positions(300)

        assert self.position_mgr.short.quantity == 0.0
        assert self.position_mgr.short.average_price == 0.0
        assert self.position_mgr.balance == self.initial_balance + 200

    def test_get_long_unrealized_pnl(self):
        self.position_mgr.fill(create_long_order(price=123.45))
        assert self.position_mgr.get_unrealized_pnl(333.12) == round(333.12 - 123.45, 4)
        assert self.position_mgr.get_unrealized_pnl(100.12) == round(100.12 - 123.45, 4)
        # fill another order at the same current price, expect pnl unchanged
        self.position_mgr.fill(create_long_order(price=333.12))
        assert self.position_mgr.get_unrealized_pnl(333.12) == round(333.12 - 123.45, 4)
        # price goes down by 100
        assert self.position_mgr.get_unrealized_pnl(233.12) == round(
            233.12 - 123.45 - 100, 4
        )
        # reduce position by 0.5, pnl is reduced
        self.position_mgr.fill(create_long_order(price=233.12, quantity=0.5, side=SELL))
        # 228.285 is average price
        assert self.position_mgr.get_unrealized_pnl(233.12) == round(
            (233.12 - 228.285) * 1.5, 4
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
        self.position_mgr.fill(create_short_order(price=200.5, quantity=0.5, side=BUY))
        assert self.position_mgr.get_unrealized_pnl(200.5) == round(
            (250.25 - 200.5) * 1.5, 4
        )

    def test_get_unrealized_pnl_with_both_long_and_short(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=250.0, quantity=0.5))
        assert self.position_mgr.get_unrealized_pnl(300) == 75.0

    def test_long_and_short_neutralized_each_other(self):
        self.position_mgr.fill(create_short_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=200.0))
        assert self.position_mgr.get_unrealized_pnl(200.0) == 0.0

    def test_buy_low_sell_high(self):
        self.position_mgr.fill(create_long_order(price=200.0))
        self.position_mgr.fill(create_short_order(price=300.0))
        # price is not important as we buy low and sell high
        assert self.position_mgr.get_unrealized_pnl(220) == 100.0
        assert self.position_mgr.get_unrealized_pnl(280) == 100.0
