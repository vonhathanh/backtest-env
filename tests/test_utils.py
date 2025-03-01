from backtest_env.utils import convert_datetime_to_nanosecond


def test_convert_time_to_nanosecond():
    input_dates = ["01/02/2024", "02-01-2024"]
    date_formats = ["%M/%d/%Y", "%d-%M-%Y"]
    expected_timestamps = [1704128460000, 1704128460000]

    for i in range(len(input_dates)):
        assert convert_datetime_to_nanosecond(input_dates[i], date_formats[i]) == expected_timestamps[i]