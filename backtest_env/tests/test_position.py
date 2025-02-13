import pytest

from backtest_env.constants import LONG, SHORT, BUY, SELL
from backtest_env.order import Order, OrderType
from backtest_env.position import LongPosition, ShortPosition


def test_increase_long_position():
    p = LongPosition()

    with pytest.raises(ValueError) as excinfo:
        p.update(Order(500.0, "BNB", BUY, OrderType.Market, LONG, 0.0)) # quantity = 0
    assert excinfo.type is ValueError

    p.update(Order(500.0, "BNB", BUY, OrderType.Market, LONG, 1.0))
    assert p.avg_price == 500.0 and p.quantity == 1.0

    p.update(Order(400.0, "BNB", BUY, OrderType.Market, LONG, 1.0))
    assert p.avg_price == 450.0 and p.quantity == 2.0

    p.update(Order(650.0, "BNB", BUY, OrderType.Market, LONG, 2.0))
    assert p.avg_price == 550.0 and p.quantity == 4.0


def test_decrease_long_position():
    p = LongPosition()

    p.update(Order(500.0, "BNB", BUY, OrderType.Market, LONG, 0.6))

    with pytest.raises(ValueError) as excinfo:
        p.update(Order(500.0, "BNB", SELL, OrderType.Market, LONG, 0.7)) # sell 0.7 while only have 0.6 bnb
    assert excinfo.type is ValueError

    p.update(Order(600.0, "BNB", SELL, OrderType.Market, LONG, 0.3))
    assert p.quantity == 0.3 and p.avg_price == 500.0


def test_increase_short_position():
    p = ShortPosition()

    with pytest.raises(ValueError) as excinfo:
        p.update(Order(500.0, "BNB", SELL, OrderType.Market, SHORT, 0.0))  # quantity = 0
    assert excinfo.type is ValueError

    p.update(Order(12.0, "BNB", SELL, OrderType.Market, SHORT, 1.0))
    assert p.avg_price == 12.0 and p.quantity == 1.0

    p.update(Order(7.0, "BNB", SELL, OrderType.Market, SHORT, 1.0))
    assert p.avg_price == 9.5 and p.quantity == 2.0

    p.update(Order(10.5, "BNB", SELL, OrderType.Market, SHORT, 2.0))
    assert p.avg_price == 10.0 and p.quantity == 4.0


def test_decrease_short_position():
    p = ShortPosition()

    p.update(Order(500.0, "BNB", SELL, OrderType.Market, SHORT, 0.6))

    with pytest.raises(ValueError) as excinfo:
        p.update(Order(500.0, "BNB", BUY, OrderType.Market, SHORT, 0.7))  # buy 0.7 while only shorted 0.6 bnb
    assert excinfo.type is ValueError

    p.update(Order(600.0, "BNB", BUY, OrderType.Market, SHORT, 0.3))
    assert p.quantity == 0.3 and p.avg_price == 500.0


def test_get_long_pnl():
    p = LongPosition()

    p.update(Order(500.0, "BNB", BUY, OrderType.Market, LONG, 1.0))
    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == 55.3
    assert p.get_pnl(452.1) == -47.9


def test_get_short_pnl():
    p = ShortPosition()

    p.update(Order(500.0, "BNB", SELL, OrderType.Market, SHORT, 1.0))

    assert p.get_pnl(500.0) == 0.0
    assert p.get_pnl(555.3) == -55.3
    assert p.get_pnl(452.1) == 47.9


def test_pnl_after_multiple_long_orders():
    p = LongPosition()

    p.update(Order(500.0, "BNB", BUY, OrderType.Market, LONG, 1.0))
    p.update(Order(560.0, "BNB", BUY, OrderType.Market, LONG, 2.0))

    assert p.get_pnl(600) == 180.0


def test_pnl_after_multiple_short_orders():
    p = ShortPosition()

    p.update(Order(500.0, "BNB", SELL, OrderType.Market, SHORT, 1.0))
    p.update(Order(560.0, "BNB", SELL, OrderType.Market, SHORT, 0.5))

    assert p.get_pnl(600.0) == -120.0
