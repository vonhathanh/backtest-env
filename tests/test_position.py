import pytest

from backtest_env.balance import Balance
from backtest_env.position import LongPosition, ShortPosition
from backtest_env.base.order import OrderSide
from utils import create_short_order, create_long_order

b = Balance(100000, 100000, 0)


def test_increase_long_position():
    p = LongPosition(b)

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_long_order(quantity=0.0))
    assert excinfo.type is AssertionError

    p.update(create_long_order(price=500.0, quantity=1.0))
    assert p.average_price == 500.0 and p.quantity == 1.0

    p.update(create_long_order(price=400.0, quantity=1.0))
    assert p.average_price == 450.0 and p.quantity == 2.0

    p.update(create_long_order(price=650.0, quantity=2.0))
    assert p.average_price == 550.0 and p.quantity == 4.0


def test_decrease_long_position():
    p = LongPosition(b)

    p.update(create_long_order(quantity=0.6, price=500.0))

    with pytest.raises(AssertionError) as excinfo:
        # sell 0.7 while only have 0.6 bnb
        p.update(create_long_order(side=OrderSide.SELL, quantity=0.7))
    assert excinfo.type is AssertionError

    p.update(create_long_order(side=OrderSide.SELL, quantity=0.3, price=600.0))
    assert p.quantity == 0.3 and p.average_price == 500.0


def test_increase_short_position():
    p = ShortPosition(b)

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_short_order(quantity=0.0))  # quantity = 0
    assert excinfo.type is AssertionError

    p.update(create_short_order(price=12.0))
    assert p.average_price == 12.0 and p.quantity == 1.0

    p.update(create_short_order(price=7.0))
    assert p.average_price == 9.5 and p.quantity == 2.0

    p.update(create_short_order(price=10.5, quantity=2.0))
    assert p.average_price == 10.0 and p.quantity == 4.0


def test_decrease_short_position():
    p = ShortPosition(b)

    p.update(create_short_order(price=500.0, quantity=0.6))

    with pytest.raises(AssertionError) as excinfo:
        # buy 0.7 while only shorted 0.6 bnb
        p.update(create_short_order(side=OrderSide.BUY, quantity=0.7))
    assert excinfo.type is AssertionError

    p.update(create_short_order(price=600.0, quantity=0.3, side=OrderSide.BUY))
    assert p.quantity == 0.3 and p.average_price == 500.0


def test_get_long_pnl():
    p = LongPosition(b)

    p.update(create_long_order(price=500.0))
    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == 55.3
    assert p.get_pnl(452.1) == -47.9


def test_get_short_pnl():
    p = ShortPosition(b)

    p.update(create_short_order(price=500.0))

    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == -55.3
    assert p.get_pnl(452.1) == 47.9


def test_pnl_after_multiple_long_orders():
    p = LongPosition(b)

    p.update(create_long_order(price=500.0))
    p.update(create_long_order(price=560.0, quantity=2.0))

    assert p.get_pnl(600) == 180.0


def test_pnl_after_multiple_short_orders():
    p = ShortPosition(b)

    p.update(create_short_order(price=500.0))
    p.update(create_short_order(price=560.0, quantity=0.5))

    assert p.get_pnl(600.0) == -120.0
