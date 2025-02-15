import pytest

from backtest_env.constants import BUY, SELL
from backtest_env.position import LongPosition, ShortPosition
from backtest_env.utils import create_short_order, create_long_order


def test_increase_long_position():
    p = LongPosition()

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_long_order(quantity=0.0))
    assert excinfo.type is AssertionError

    p.update(create_long_order(price=500.0, quantity=1.0))
    assert p.avg_price == 500.0 and p.quantity == 1.0

    p.update(create_long_order(price=400.0, quantity=1.0))
    assert p.avg_price == 450.0 and p.quantity == 2.0

    p.update(create_long_order(price=650.0, quantity=2.0))
    assert p.avg_price == 550.0 and p.quantity == 4.0


def test_decrease_long_position():
    p = LongPosition()

    p.update(create_long_order(quantity=0.6, price=500.0))

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_long_order(side=SELL, quantity=0.7)) # sell 0.7 while only have 0.6 bnb
    assert excinfo.type is AssertionError

    p.update(create_long_order(side=SELL, quantity=0.3, price=600.0))
    assert p.quantity == 0.3 and p.avg_price == 500.0


def test_increase_short_position():
    p = ShortPosition()

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_short_order(quantity=0.0))  # quantity = 0
    assert excinfo.type is AssertionError

    p.update(create_short_order(price=12.0))
    assert p.avg_price == 12.0 and p.quantity == 1.0

    p.update(create_short_order(price=7.0))
    assert p.avg_price == 9.5 and p.quantity == 2.0

    p.update(create_short_order(price=10.5, quantity=2.0))
    assert p.avg_price == 10.0 and p.quantity == 4.0


def test_decrease_short_position():
    p = ShortPosition()

    p.update(create_short_order(price=500.0, quantity=0.6))

    with pytest.raises(AssertionError) as excinfo:
        p.update(create_short_order(side=BUY, quantity=0.7))  # buy 0.7 while only shorted 0.6 bnb
    assert excinfo.type is AssertionError

    p.update(create_short_order(price=600.0, quantity=0.3, side=BUY))
    assert p.quantity == 0.3 and p.avg_price == 500.0


def test_get_long_pnl():
    p = LongPosition()

    p.update(create_long_order(price=500.0))
    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == 55.3
    assert p.get_pnl(452.1) == -47.9


def test_get_short_pnl():
    p = ShortPosition()

    p.update(create_short_order(price=500.0))

    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == -55.3
    assert p.get_pnl(452.1) == 47.9


def test_pnl_after_multiple_long_orders():
    p = LongPosition()

    p.update(create_long_order(price=500.0))
    p.update(create_long_order(price=560.0, quantity=2.0))

    assert p.get_pnl(600) == 180.0


def test_pnl_after_multiple_short_orders():
    p = ShortPosition()

    p.update(create_short_order(price=500.0))
    p.update(create_short_order(price=560.0, quantity=0.5))

    assert p.get_pnl(600.0) == -120.0
