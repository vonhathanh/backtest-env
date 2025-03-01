from unittest.mock import patch

import numpy as np

from backtest_env.price import PriceDataSet, Price

mock_data = np.array([[1740589200000, 10.0, 11.0, 9.0, 9.5, 1740675599999],
                      [1740675600000, 9.5, 12.0, 9.4, 10, 1740761999999]])


def assert_price(price: Price, true_value: list | np.ndarray):
    assert price.open_time == int(true_value[0])
    assert price.open == float(true_value[1])
    assert price.high == float(true_value[2])
    assert price.low == float(true_value[3])
    assert price.close == float(true_value[4])
    assert price.close_time == int(true_value[5])


@patch("backtest_env.price.load_price_data")
def test_get_current_price(mock_utils):
    mock_utils.return_value = mock_data
    dataset = PriceDataSet("BNB", "1h", "2025-02-27", "2025-02-28")

    assert len(dataset) == 2

    dataset.step()
    current_price = dataset.get_current_price()
    assert_price(current_price, mock_data[0])

    dataset.step()
    current_price = dataset.get_current_price()
    assert_price(current_price, mock_data[1])


@patch("backtest_env.price.load_price_data")
def test_get_item(mock_utils):
    mock_utils.return_value = mock_data
    dataset = PriceDataSet("BNB", "1h", "2025-02-27", "2025-02-28")

    price = dataset[0]
    assert_price(price, mock_data[0])


@patch("backtest_env.price.load_price_data")
def test_get_last_price(mock_utils):
    mock_utils.return_value = mock_data
    dataset = PriceDataSet("BNB", "1h", "2025-02-27", "2025-02-28")

    price = dataset.get_last_price()
    assert_price(price, mock_data[1])