from unittest.mock import Mock

import pytest

from backtest_env.base.order import OrderType, OrderSide, PositionSide, Order
from backtest_env.order_manager import OrderManager
from backtest_env.orders.limit import LimitOrder
from backtest_env.orders.oco import OneCancelOtherOrder
from backtest_env.price import Price
from utils import create_long_order


class TestOrderManager:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.data = Mock()
        self.position_mgr = Mock()
        self.order_mgr = OrderManager(self.position_mgr, self.data)
        self.data.get_current_price.return_value = Price(0, 100, 100, 100, 100, 0)
        self.data.get_close_time.return_value = 100
        yield
        # Teardown code
        self.order_mgr.unsubscribe()
        self.order_mgr = None
        self.position_mgr = None
        self.data = None

    @staticmethod
    def assert_order_eq(src_order: Order, tgt_order: Order):
        assert src_order.side == tgt_order.side
        assert src_order.price == tgt_order.price
        assert src_order.quantity == tgt_order.quantity
        assert src_order.position_side == tgt_order.position_side
        assert src_order.type == tgt_order.type

    def test_get_open_orders(self):
        # empty orders
        orders = self.order_mgr.get_orders_by_side(OrderSide.BUY)
        assert len(orders) == 0

        # 1 buy and 0 sell order
        self.order_mgr.add_order(create_long_order(side=OrderSide.BUY))
        long_orders = self.order_mgr.get_orders_by_side(OrderSide.BUY)
        short_orders = self.order_mgr.get_orders_by_side(OrderSide.SELL)
        assert len(long_orders) == 1 and len(short_orders) == 0

        # add new sell order
        self.order_mgr.add_order(create_long_order(side=OrderSide.SELL))
        short_orders = self.order_mgr.get_orders_by_side(OrderSide.SELL)
        assert len(short_orders) == 1

        # more than 1 sell order
        self.order_mgr.add_order(create_long_order(side=OrderSide.SELL))
        short_orders = self.order_mgr.get_orders_by_side(OrderSide.SELL)
        assert len(short_orders) == 2

    def test_process_orders(self):
        market_order = create_long_order(side=OrderSide.BUY, price=100.0)
        limit_order = LimitOrder(OrderSide.BUY, 120.0, "X", 120.0, PositionSide.LONG)

        self.order_mgr.add_orders([market_order, limit_order])

        # force price to return 100 so limit order not filled
        self.order_mgr.price_dataset.get_current_price.return_value = Price(
            0, 100, 100, 100, 100, 0
        )

        # process only market order so limit order will stay
        self.order_mgr.process_orders()
        orders = self.order_mgr.get_all_orders()
        assert len(orders) == 1 and orders[0].type == OrderType.Limit

        # force price to contain limit order price, so it can be processed
        self.order_mgr.price_dataset.get_current_price.return_value = Price(
            0, 110, 120, 100, 110, 0
        )

        self.order_mgr.process_orders()
        assert len(self.order_mgr.get_all_orders()) == 0

    def test_oco_stoploss(self):
        order = OneCancelOtherOrder(
            90,
            0,
            OrderSide.BUY,
            amount_in_usd=300.0,
            symbol="X",
            price=100.0,
            position_side=PositionSide.LONG,
        )
        self.order_mgr.add_order(order)
        self.order_mgr.process_orders()

        orders = self.order_mgr.get_all_orders()
        # stoploss & take-profit are added after oco is filled
        assert len(orders) == 1
        self.assert_order_eq(
            orders[0], LimitOrder(OrderSide.SELL, 270.0, "X", 90, PositionSide.LONG)
        )

    def test_oco_take_profit(self):
        order = OneCancelOtherOrder(
            0,
            110,
            OrderSide.BUY,
            amount_in_usd=300.0,
            symbol="X",
            price=100.0,
            position_side=PositionSide.LONG,
        )
        self.order_mgr.add_order(order)
        self.order_mgr.process_orders()

        orders = self.order_mgr.get_all_orders()
        # stoploss & take-profit are added after oco is filled
        assert len(orders) == 1
        self.assert_order_eq(
            orders[0], LimitOrder(OrderSide.SELL, 330.0, "X", 110, PositionSide.LONG)
        )

    def test_oco_both_sl_and_tp(self):
        order = OneCancelOtherOrder(
            90,
            110,
            OrderSide.BUY,
            amount_in_usd=300.0,
            symbol="X",
            price=100.0,
            position_side=PositionSide.LONG,
        )
        self.order_mgr.add_order(order)
        self.order_mgr.process_orders()

        orders = self.order_mgr.get_all_orders()
        # stoploss & take-profit are added after oco is filled
        assert len(orders) == 2
        self.assert_order_eq(
            orders[0], LimitOrder(OrderSide.SELL, 270.0, "X", 90, PositionSide.LONG)
        )
        self.assert_order_eq(
            orders[1], LimitOrder(OrderSide.SELL, 330.0, "X", 110, PositionSide.LONG)
        )
